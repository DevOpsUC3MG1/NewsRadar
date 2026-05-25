import os
import sys
import json
import pytest
import pytest_asyncio
from datetime import datetime
from pathlib import Path
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch as _patch

# Ensure the backend directory is on the Python path
_backend_root = str(Path(__file__).resolve().parents[1])
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

os.environ.setdefault("ENV", "testing")

# Override DB URL to use SQLite in-memory — no Postgres needed
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

# Ensure Gmail env vars are set so import doesn't crash
os.environ.setdefault("GMAIL_SENDER", "test@newsradar.com")
os.environ.setdefault("GMAIL_APP_PASSWORD", "test_placeholder")

# Mock email sending functions so tests don't hit real SMTP
_patch("newsradar_api.app.main.send_verification_email", return_value=None).start()
_patch("newsradar_api.app.main.send_reset_password_email", return_value=None).start()


# ======================================================================
#  In-memory MongoDB mock — stores everything in dicts, supports the
#  subset of operations used by NewsRadar (stats CRUD, analytics).
# ======================================================================

class _MockCursor:
    def __init__(self, docs, sort_key=None, sort_dir=-1):
        self._docs = list(docs)
        self._sort_key = sort_key
        self._sort_dir = sort_dir

    def sort(self, key, direction=-1):
        return _MockCursor(self._docs, sort_key=key, sort_dir=direction)

    async def to_list(self, length=None):
        docs = self._docs
        if self._sort_key:
            docs = sorted(
                docs,
                key=lambda d: d.get(self._sort_key, 0),
                reverse=(self._sort_dir == -1),
            )
        if length is not None:
            docs = docs[:length]
        return docs


def _normalize_dt(val):
    """Make offset-naive datetimes offset-aware (UTC) for comparison."""
    if isinstance(val, datetime) and val.tzinfo is None:
        return val.replace(tzinfo=timezone.utc)
    return val


def _match_doc(doc, filter):
    """Check whether a document matches a simple MongoDB filter dict."""
    if filter is None:
        return True
    for key, value in filter.items():
        dv = doc.get(key)
        if not isinstance(value, dict):
            if dv != value:
                return False
        else:
            if "$in" in value and dv not in value["$in"]:
                return False
            dv = _normalize_dt(dv)
            if "$gte" in value:
                cmp = _normalize_dt(value["$gte"])
                if dv is None or dv < cmp:
                    return False
            if "$lte" in value:
                cmp = _normalize_dt(value["$lte"])
                if dv is None or dv > cmp:
                    return False
    return True


class _MockMongoCollection:
    def __init__(self):
        self._docs = {}
        self._next_id = 1

    def _apply_update(self, doc, update):
        doc = dict(doc)
        for op, fields in update.items():
            if op == "$set":
                for k, v in fields.items():
                    doc[k] = v
            elif op == "$inc":
                for k, v in fields.items():
                    doc[k] = doc.get(k, 0) + v
        return doc

    async def find_one(self, filter=None, sort=None):
        matches = [dict(d) for d in self._docs.values() if _match_doc(d, filter)]
        if not matches:
            return None
        if sort:
            key, direction = sort[0]
            matches.sort(key=lambda d: d.get(key, 0), reverse=(direction == -1))
            return matches[-1]
        return matches[0]

    def find(self, filter=None, projection=None):
        docs = [dict(d) for d in self._docs.values() if _match_doc(d, filter)]
        if projection:
            docs = [{k: d[k] for k in projection if k in d} for d in docs]
        return _MockCursor(docs)

    async def insert_one(self, doc):
        entry = dict(doc)
        if "_id" not in entry:
            entry["_id"] = self._next_id
            self._next_id += 1
        else:
            existing_id = entry["_id"]
            if isinstance(existing_id, int) and existing_id >= self._next_id:
                self._next_id = existing_id + 1
        self._docs[entry["_id"]] = entry
        return type("_result", (), {"inserted_id": entry["_id"], "acknowledged": True})()

    async def update_one(self, filter, update, upsert=False):
        for doc_id, doc in list(self._docs.items()):
            if _match_doc(doc, filter):
                self._docs[doc_id] = self._apply_update(doc, update)
                return type("_result", (), {"matched_count": 1, "modified_count": 1})()
        if upsert:
            doc = self._apply_update(
                {k.split(".")[-1]: v for k, v in update.get("$set", {}).items()},
                update,
            )
            await self.insert_one(doc)
        return type("_result", (), {"matched_count": 0, "modified_count": 0})()

    async def delete_one(self, filter):
        for doc_id, doc in list(self._docs.items()):
            if _match_doc(doc, filter):
                del self._docs[doc_id]
                return type("_result", (), {"deleted_count": 1})()
        return type("_result", (), {"deleted_count": 0})()

    async def delete_many(self, filter):
        to_del = [doc_id for doc_id, doc in self._docs.items() if _match_doc(doc, filter)]
        for doc_id in to_del:
            del self._docs[doc_id]
        return type("_result", (), {"deleted_count": len(to_del)})()

    async def count_documents(self, filter):
        return sum(1 for d in self._docs.values() if _match_doc(d, filter))

    def aggregate(self, pipeline):
        docs = list(self._docs.values())
        for stage in pipeline:
            if "$match" in stage:
                docs = [d for d in docs if _match_doc(d, stage["$match"])]
            elif "$group" in stage:
                id_field = stage["$group"]["_id"]
                groups = {}
                for d in docs:
                    key = d.get(id_field, "Unknown")
                    if key not in groups:
                        groups[key] = {"_id": key}
                    for alias, expr in stage["$group"].items():
                        if alias == "_id":
                            continue
                        if "$sum" in expr:
                            groups[key][alias] = groups[key].get(alias, 0) + 1
                docs = list(groups.values())
        return _MockCursor(docs)


class _MockMongoDB:
    def __init__(self):
        self._collections = {}

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return self._collections.setdefault(name, _MockMongoCollection())

    def __getitem__(self, name):
        return self._collections.setdefault(name, _MockMongoCollection())


_mock_mongo = _MockMongoDB()


async def _get_mock_mongo():
    return _mock_mongo


# Import app and wire up overrides
from newsradar_api.app.main import app
from newsradar_api.app.database_mongodb import get_mongo_db

app.dependency_overrides[get_mongo_db] = _get_mock_mongo

# Override databases to use SQLite
from newsradar_api.app.database import get_db, get_engine, Base


# --- DB INIT (async, session-scoped) ---

@pytest_asyncio.fixture(scope="session")
async def db_init():
    from newsradar_api.app.main import create_seed_data
    from newsradar_api.app.seed import run as seed_run
    eng = get_engine()
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await create_seed_data()
    await seed_run()
    yield


# --- ASYNC HTTP CLIENT via ASGITransport (in-process) ---

@pytest_asyncio.fixture(scope="session")
async def client(db_init):
    # Re-apply the MongoDB override (app might be re-imported)
    app.dependency_overrides[get_mongo_db] = _get_mock_mongo
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# --- AUTH FIXTURES ---

@pytest_asyncio.fixture(scope="session")
async def gestor_token(client):
    resp = await client.post("/api/v1/auth/login", json={
        "email": "admin@newsradar.com",
        "password": "admin123",
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def gestor_headers(gestor_token):
    return {"Authorization": f"Bearer {gestor_token}"}


@pytest_asyncio.fixture
async def clean_alerts(client, gestor_headers):
    resp = await client.get("/api/v1/users/1/alerts", headers=gestor_headers)
    for alert in resp.json():
        await client.delete(f"/api/v1/users/1/alerts/{alert['id']}", headers=gestor_headers)
    yield


# --- FIXTURES DE USUARIOS (RF-09) ---

@pytest.fixture
def fixture_user_lector():
    return {
        "id": 1,
        "username": "lector_test",
        "email": "lector@newsradar.es",
        "role": "Lector",
        "is_active": True,
    }


@pytest.fixture
def fixture_user_gestor():
    return {
        "id": 2,
        "username": "admin_news",
        "email": "gestor@newsradar.es",
        "role": "Gestor",
        "is_active": True,
    }


# --- FIXTURES DE ALERTAS (RF-01, RF-02) ---

@pytest.fixture
def fixture_alerta_base():
    return {
        "id": 101,
        "name": "Crisis Energética",
        "keyword": "luz",
        "description": "Monitorización de precios de energía",
        "category": "Economía",
        "keywords_ia": ["electricidad", "gas", "factura", "renovables"],
        "user_id": 2,
        "created_at": datetime.now().isoformat(),
    }


# --- FIXTURES DE NOTICIAS/FUENTES (RF-05, RF-07) ---

@pytest.fixture
def fixture_noticia_rss():
    return {
        "id_mongo": "65f1a...",
        "title": "El precio de la luz sube un 10%",
        "content": "La escalada de precios continúa en el sector energético...",
        "source": "El País",
        "url": "https://elpais.com/economia/noticia1",
        "category_iptc": "Economía",
        "published_at": datetime.now().isoformat(),
    }


# --- FIXTURES DE CLIENTE API (legacy: headers mockeados) ---

@pytest.fixture
def mock_headers_auth(fixture_user_gestor):
    return {
        "Authorization": "Bearer token_ficticio_gestor",
        "Content-Type": "application/json",
    }


# --- FIXTURES DE ARCHIVOS ---

@pytest.fixture
def load_valid_users():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "fixtures", "users_valid.json")
    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)


@pytest.fixture
def mock_rss_xml():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    xml_path = os.path.join(base_dir, "fixtures", "feed_falso.xml")
    with open(xml_path, "r", encoding="utf-8") as file:
        return file.read()
