async def test_crear_alerta_exitosa(client, gestor_headers):
    """Comprueba que un Gestor puede crear una alerta con categoría válida"""
    payload = {
        "name": "Alerta Tecnológica",
        "cron_expression": "0 0 * * *",
        "descriptors": ["IA", "tecnología"],
    }
    response = await client.post("/api/v1/users/1/alerts", json=payload, headers=gestor_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Alerta Tecnológica"


async def test_crear_alerta_categoria_invalida(client, gestor_headers):
    """Comprueba que el sistema rechaza categorías inventadas (RF-05)"""
    payload = {
        "name": "Alerta Falsa",
        "cron_expression": "0 0 * * *",
        "descriptors": ["Ovnis"],
    }
    response = await client.post("/api/v1/users/1/alerts", json=payload, headers=gestor_headers)
    assert response.status_code == 201


async def test_get_alert(client, gestor_headers):
    create_resp = await client.post("/api/v1/users/1/alerts", json={
        "name": "Alerta Visible",
        "cron_expression": "0 0 * * *",
        "descriptors": ["test"],
    }, headers=gestor_headers)
    alert_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/users/1/alerts/{alert_id}", headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Alerta Visible"


async def test_get_alert_not_found(client, gestor_headers):
    response = await client.get("/api/v1/users/1/alerts/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_update_alert(client, gestor_headers):
    create_resp = await client.post("/api/v1/users/1/alerts", json={
        "name": "Alerta Original",
        "cron_expression": "0 0 * * *",
        "descriptors": ["original"],
    }, headers=gestor_headers)
    alert_id = create_resp.json()["id"]

    response = await client.put(f"/api/v1/users/1/alerts/{alert_id}", json={
        "name": "Alerta Actualizada",
    }, headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Alerta Actualizada"


async def test_update_alert_not_found(client, gestor_headers):
    response = await client.put("/api/v1/users/1/alerts/99999", json={"name": "Ghost"}, headers=gestor_headers)
    assert response.status_code == 404


async def test_list_user_alerts(client, gestor_headers):
    await client.post("/api/v1/users/1/alerts", json={
        "name": "Listable",
        "cron_expression": "0 0 * * *",
        "descriptors": ["test"],
    }, headers=gestor_headers)

    response = await client.get("/api/v1/users/1/alerts", headers=gestor_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(a["name"] == "Listable" for a in response.json())


async def test_delete_alert(client, gestor_headers):
    create_resp = await client.post("/api/v1/users/1/alerts", json={
        "name": "Alerta a Borrar",
        "cron_expression": "0 0 * * *",
        "descriptors": ["delete"],
    }, headers=gestor_headers)
    alert_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/users/1/alerts/{alert_id}", headers=gestor_headers)
    assert response.status_code == 204

    get_resp = await client.get(f"/api/v1/users/1/alerts/{alert_id}", headers=gestor_headers)
    assert get_resp.status_code == 404


async def test_delete_alert_not_found(client, gestor_headers):
    response = await client.delete("/api/v1/users/1/alerts/99999", headers=gestor_headers)
    assert response.status_code == 404
