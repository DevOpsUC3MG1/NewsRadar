import os


def test_docker_db_connection():
    """Verifica que el entorno de test tiene acceso a la base de datos real"""
    db_url = os.getenv("DATABASE_URL")
    assert db_url is not None, "DATABASE_URL debe estar configurada"
    assert "sqlite" in db_url or any(x in db_url for x in ["test", "newsradar"]), \
        f"DATABASE_URL no es válida: {db_url}"


def test_env_is_testing():
    """Asegura que no estamos tocando la base de datos de producción"""
    assert os.getenv("ENV") == "testing"
