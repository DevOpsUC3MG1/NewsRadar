import pytest

def test_crear_alerta_exitosa(client):
    """Comprueba que un Gestor puede crear una alerta con categoría válida"""
    # Simulamos el token de un Gestor
    headers = {"Authorization": "Bearer token_falso_gestor"}
    payload = {
        "name": "Alerta Tecnológica",
        "keyword": "IA",
        "category": "Tecnología" # Categoría válida
    }
    
    response = client.post("/api/v1/alerts", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Alerta Tecnológica"

def test_crear_alerta_categoria_invalida(client):
    """Comprueba que el sistema rechaza categorías inventadas (RF-05)"""
    headers = {"Authorization": "Bearer token_falso_gestor"}
    payload = {
        "name": "Alerta Falsa",
        "keyword": "Ovnis",
        "category": "CategoríaInventada" # El backend debe rechazar esto
    }
    
    response = client.post("/api/v1/alerts", json=payload, headers=headers)
    assert response.status_code == 422 # Unprocessable Entity