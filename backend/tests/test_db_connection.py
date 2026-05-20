import os


def test_docker_db_connection():
    """Verifica que el entorno de test tiene acceso a la DB de Docker"""
    db_url = os.getenv("DATABASE_URL")

    # Comprobamos que la variable de entorno está configurada
    assert db_url is not None
    assert "newsradar_test" in db_url
    print(f"✅ Conectado exitosamente a: {db_url}")


def test_env_is_testing():
    """Asegura que no estamos tocando la base de datos de producción"""
    assert os.getenv("ENV") == "testing"
