import pytest
from datetime import datetime

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
        "category": "Economía", # Categoría de primer nivel IPTC
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

# --- FIXTURES DE CLIENTE API (Necesario para el Sprint 1) ---

@pytest.fixture
def mock_headers_auth(fixture_user_gestor):
    """Simula los headers de autorización JWT para las pruebas de API"""
    return {
        "Authorization": "Bearer token_ficticio_gestor",
        "Content-Type": "application/json"
    }
@pytest.fixture(scope="session")
def db_engine():
    """
    Configuración de la conexión a DB para todos los tests.
    Avisar al M1 cuando elija el ORM (SQLAlchemy/Tortoise) para completar.
    """
    # Por ahora solo simulamos la preparación
    yield "engine_ready"
    print("\nCerrando conexión de test...")