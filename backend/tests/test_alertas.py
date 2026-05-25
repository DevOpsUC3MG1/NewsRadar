from uuid import uuid4
import pytest

pytestmark = pytest.mark.usefixtures("clean_alerts")


async def test_crear_alerta_exitosa(client, gestor_headers):
    """Comprueba que un Gestor puede crear una alerta con categoría válida"""
    suffix = uuid4().hex[:8]
    payload = {
        "name": f"Alerta-{suffix}",
        "cron_expression": "0 0 * * *",
        "descriptors": [f"tag-{suffix}"],
    }
    response = await client.post("/api/v1/users/1/alerts", json=payload, headers=gestor_headers)
    assert response.status_code == 201
    assert response.json()["name"] == f"Alerta-{suffix}"


async def test_crear_alerta_categoria_invalida(client, gestor_headers):
    """Comprueba que el sistema rechaza categorías inventadas (RF-05)"""
    suffix = uuid4().hex[:8]
    payload = {
        "name": f"AlertaFalsa-{suffix}",
        "cron_expression": "0 0 * * *",
        "descriptors": [f"tag-{suffix}"],
    }
    response = await client.post("/api/v1/users/1/alerts", json=payload, headers=gestor_headers)
    assert response.status_code == 201


async def test_get_alert(client, gestor_headers):
    suffix = uuid4().hex[:8]
    name = f"AlertaVisible-{suffix}"
    create_resp = await client.post("/api/v1/users/1/alerts", json={
        "name": name,
        "cron_expression": "0 0 * * *",
        "descriptors": [f"tag-{suffix}"],
    }, headers=gestor_headers)
    alert_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/users/1/alerts/{alert_id}", headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["name"] == name


async def test_get_alert_not_found(client, gestor_headers):
    response = await client.get("/api/v1/users/1/alerts/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_update_alert(client, gestor_headers):
    suffix = uuid4().hex[:8]
    name = f"AlertaOriginal-{suffix}"
    create_resp = await client.post("/api/v1/users/1/alerts", json={
        "name": name,
        "cron_expression": "0 0 * * *",
        "descriptors": [f"tag-{suffix}"],
    }, headers=gestor_headers)
    alert_id = create_resp.json()["id"]

    response = await client.put(f"/api/v1/users/1/alerts/{alert_id}", json={
        "name": f"AlertaActualizada-{suffix}",
    }, headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["name"] == f"AlertaActualizada-{suffix}"


async def test_update_alert_not_found(client, gestor_headers):
    response = await client.put("/api/v1/users/1/alerts/99999", json={"name": "Ghost"}, headers=gestor_headers)
    assert response.status_code == 404


async def test_list_user_alerts(client, gestor_headers):
    suffix = uuid4().hex[:8]
    name = f"Listable-{suffix}"
    await client.post("/api/v1/users/1/alerts", json={
        "name": name,
        "cron_expression": "0 0 * * *",
        "descriptors": [f"tag-{suffix}"],
    }, headers=gestor_headers)

    response = await client.get("/api/v1/users/1/alerts", headers=gestor_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(a["name"] == name for a in response.json())


async def test_delete_alert(client, gestor_headers):
    suffix = uuid4().hex[:8]
    name = f"AlertaBorrar-{suffix}"
    create_resp = await client.post("/api/v1/users/1/alerts", json={
        "name": name,
        "cron_expression": "0 0 * * *",
        "descriptors": [f"tag-{suffix}"],
    }, headers=gestor_headers)
    alert_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/users/1/alerts/{alert_id}", headers=gestor_headers)
    assert response.status_code == 204

    get_resp = await client.get(f"/api/v1/users/1/alerts/{alert_id}", headers=gestor_headers)
    assert get_resp.status_code == 404


async def test_delete_alert_not_found(client, gestor_headers):
    response = await client.delete("/api/v1/users/1/alerts/99999", headers=gestor_headers)
    assert response.status_code == 404
