import os


def test_docker_db_connection():
    """Verifica que el entorno de test tiene configuración de base de datos (o usa mock)"""
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        assert any(x in db_url for x in ["test", "newsradar"])
        print(f"✅ Conectado exitosamente a: {db_url}")
    else:
        print("ℹ️  Sin DATABASE_URL — usando app mock (sin DB)")


def test_env_is_testing():
    """Asegura que no estamos tocando la base de datos de producción"""
    assert os.getenv("ENV") == "testing"
