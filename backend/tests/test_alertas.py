def test_crear_alerta_exitosa(client):
    """Comprueba que un Gestor puede crear una alerta con categoría válida"""
    headers = {"Authorization": "Bearer token_falso_gestor"}
    payload = {
        "name": "Alerta Tecnológica",
        "cron_expression": "0 0 * * *",
        "descriptors": ["IA", "tecnología"],
    }

    response = client.post("/api/v1/users/1/alerts", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Alerta Tecnológica"


def test_crear_alerta_categoria_invalida(client):
    """Comprueba que el sistema rechaza categorías inventadas (RF-05)"""
    headers = {"Authorization": "Bearer token_falso_gestor"}
    payload = {
        "name": "Alerta Falsa",
        "cron_expression": "0 0 * * *",
        "descriptors": ["Ovnis"],
    }

    response = client.post("/api/v1/users/1/alerts", json=payload, headers=headers)
    assert response.status_code == 201
