import pytest

@pytest.fixture
def lector_ficticio():
    """Esta fixture prepara un diccionario con datos de un usuario normal"""
    return {
        "username": "pepito_test",
        "email": "pepito@newsradar.es",
        "role": "Lector",
        "is_active": True
    }