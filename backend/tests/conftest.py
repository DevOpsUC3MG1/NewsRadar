import os
import json
import nest_asyncio
import pytest
from datetime import datetime
from fastapi.testclient import TestClient

nest_asyncio.apply()


# --- FIXTURES DE USUARIOS (RF-09) ---

@pytest.fixture
def fixture_user_lector():
    """Simula un usuario con rol Lector (solo visualiza)"""
    return {
        "id": 1,
        "username": "lector_test",
        "email": "lector@newsradar.es",
        "role": "Lector",
        "is_active": True
    }


@pytest.fixture
def fixture_user_gestor():
    """Simula un usuario con rol Gestor (puede crear alertas y fuentes)"""
    return {
        "id": 2,
        "username": "admin_news",
        "email": "gestor@newsradar.es",
        "role": "Gestor",
        "is_active": True
    }


# --- FIXTURES DE ALERTAS (RF-01, RF-02) ---

@pytest.fixture
def fixture_alerta_base():
    """Simula una alerta recién creada con sus sinónimos de IA"""
    return {
        "id": 101,
        "name": "Crisis Energética",
        "keyword": "luz",
        "description": "Monitorización de precios de energía",
        "category": "Economía",
        "keywords_ia": ["electricidad", "gas", "factura", "renovables"],
        "user_id": 2,
        "created_at": datetime.now().isoformat()
    }


# --- FIXTURES DE NOTICIAS/FUENTES (RF-05, RF-07) ---

@pytest.fixture
def fixture_noticia_rss():
    """Simula una noticia capturada de un feed RSS"""
    return {
        "id_mongo": "65f1a...",
        "title": "El precio de la luz sube un 10%",
        "content": "La escalada de precios continúa en el sector energético...",
        "source": "El País",
        "url": "https://elpais.com/economia/noticia1",
        "category_iptc": "Economía",
        "published_at": datetime.now().isoformat()
    }


# --- FIXTURES DE CLIENTE API ---

@pytest.fixture
def mock_headers_auth(fixture_user_gestor):
    """Simula los headers de autorización JWT para las pruebas de API"""
    return {
        "Authorization": "Bearer token_ficticio_gestor",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="session")
def db_engine():
    """Configuración de la conexión a DB para todos los tests."""
    yield "engine_ready"
    print("\nCerrando conexión de test...")


@pytest.fixture
def client():
    """Fixture para simular peticiones a la API"""
    from newsradar_api.app.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture
def load_valid_users():
    """Lee el archivo JSON de usuarios válidos y lo devuelve como diccionario"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "fixtures", "users_valid.json")

    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)


@pytest.fixture
def mock_rss_xml():
    """Lee el archivo XML falso para simular una respuesta de un feed RSS"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    xml_path = os.path.join(base_dir, "fixtures", "feed_falso.xml")

    with open(xml_path, "r", encoding="utf-8") as file:
        return file.read()
