import os
import sys
import json
import asyncio
import pytest
import pytest_asyncio
from datetime import datetime
from pathlib import Path
from httpx import ASGITransport, AsyncClient

# Ensure the backend directory is on the Python path
_backend_root = str(Path(__file__).resolve().parents[1])
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

os.environ.setdefault("ENV", "testing")


# --- DB INIT (async, session-scoped) ---

@pytest_asyncio.fixture(scope="session")
async def db_init():
    from newsradar_api.app.main import create_seed_data
    from newsradar_api.app.database import get_engine, Base
    eng = get_engine()
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await create_seed_data()
    yield


# --- ASYNC HTTP CLIENT (session-scoped) ---

@pytest_asyncio.fixture(scope="session")
async def client(db_init):
    from newsradar_api.app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# --- AUTH FIXTURES ---

@pytest_asyncio.fixture
async def gestor_token(client):
    resp = await client.post("/api/v1/auth/login", json={
        "email": "admin@newsradar.com",
        "password": "admin123",
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture
def gestor_headers(gestor_token):
    return {"Authorization": f"Bearer {gestor_token}"}


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
