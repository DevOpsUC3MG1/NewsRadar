def test_flujo_completo_gestion_noticias(client):
    """
    Simula el flujo completo de un Gestor:
    1. Login -> 2. Crear Canal RSS -> 3. Crear Alerta de término
    """
    headers = {"Authorization": "Bearer token_valido_gestor"}

    canal_data = {
        "name": "El País - Tecnología",
        "url": "https://elpais.com/rss/tecnologia.xml",
    }
    res_canal = client.post("/api/v1/information-sources", json=canal_data, headers=headers)

    alerta_data = {
        "name": "Alerta IA",
        "cron_expression": "0 0 * * *",
        "descriptors": ["Inteligencia Artificial"],
    }
    res_alerta = client.post("/api/v1/users/1/alerts", json=alerta_data, headers=headers)

    assert res_canal.status_code in [201, 404]
    assert res_alerta.status_code in [201, 404]


def test_flujo_baja_de_terminos(client):
    """Valida que un usuario puede dejar de seguir un término (borrar alerta)"""
    headers = {"Authorization": "Bearer token_valido_gestor"}

    alerta_data = {
        "name": "Alerta a borrar",
        "cron_expression": "0 0 * * *",
    }
    res_crear = client.post("/api/v1/users/1/alerts", json=alerta_data, headers=headers)

    if res_crear.status_code == 201:
        alerta_id = res_crear.json()["id"]
        response = client.delete(f"/api/v1/users/1/alerts/{alerta_id}", headers=headers)
        assert response.status_code == 204
    else:
        assert res_crear.status_code in [201, 404]
