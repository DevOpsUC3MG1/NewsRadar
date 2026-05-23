"""Tests for Notifications CRUD — MongoDB-backed, requires an alert"""


from uuid import uuid4


async def _create_alert(client, gestor_headers):
    name = f"Notif Alert {uuid4().hex[:8]}"
    payload = {
        "name": name,
        "cron_expression": "0 0 * * *",
        "descriptors": ["test"],
    }
    resp = await client.post("/api/v1/users/1/alerts", json=payload, headers=gestor_headers)
    assert resp.status_code == 201, f"Alert creation failed: {resp.text}"
    return resp.json()["id"]


async def test_create_notification(client, gestor_headers):
    alert_id = await _create_alert(client, gestor_headers)
    now = "2025-01-01T00:00:00Z"
    payload = {
        "timestamp": now,
        "metrics": [{"name": "articles_detected", "value": 5}],
        "title": "Notificación de prueba",
        "content": "Contenido de prueba",
        "news": [
            {
                "title": "Noticia test",
                "link": "https://example.com",
                "source_name": "Test Source",
                "category": "Technology",
                "published": now,
                "description": "Descripción test",
            }
        ],
    }
    response = await client.post(
        f"/api/v1/users/1/alerts/{alert_id}/notifications",
        json=payload,
        headers=gestor_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Notificación de prueba"
    assert data["alert_id"] == alert_id


async def test_list_notifications(client, gestor_headers):
    alert_id = await _create_alert(client, gestor_headers)
    now = "2025-01-01T00:00:00Z"
    await client.post(
        f"/api/v1/users/1/alerts/{alert_id}/notifications",
        json={"timestamp": now, "title": "Listable"},
        headers=gestor_headers,
    )

    response = await client.get(
        f"/api/v1/users/1/alerts/{alert_id}/notifications",
        headers=gestor_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(n["title"] == "Listable" for n in data)


async def test_get_notification(client, gestor_headers):
    alert_id = await _create_alert(client, gestor_headers)
    now = "2025-01-01T00:00:00Z"
    create_resp = await client.post(
        f"/api/v1/users/1/alerts/{alert_id}/notifications",
        json={"timestamp": now, "title": "Visible"},
        headers=gestor_headers,
    )
    notif_id = create_resp.json()["id"]

    response = await client.get(
        f"/api/v1/users/1/alerts/{alert_id}/notifications/{notif_id}",
        headers=gestor_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Visible"


async def test_get_notification_not_found_alert(client, gestor_headers):
    response = await client.get(
        "/api/v1/users/1/alerts/99999/notifications/1",
        headers=gestor_headers,
    )
    assert response.status_code == 404


async def test_get_notification_not_found_notif(client, gestor_headers):
    alert_id = await _create_alert(client, gestor_headers)
    response = await client.get(
        f"/api/v1/users/1/alerts/{alert_id}/notifications/99999",
        headers=gestor_headers,
    )
    assert response.status_code == 404


async def test_update_notification(client, gestor_headers):
    alert_id = await _create_alert(client, gestor_headers)
    now = "2025-01-01T00:00:00Z"
    create_resp = await client.post(
        f"/api/v1/users/1/alerts/{alert_id}/notifications",
        json={"timestamp": now, "title": "Original"},
        headers=gestor_headers,
    )
    notif_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/v1/users/1/alerts/{alert_id}/notifications/{notif_id}",
        json={"title": "Actualizada"},
        headers=gestor_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Actualizada"


async def test_update_notification_not_found(client, gestor_headers):
    alert_id = await _create_alert(client, gestor_headers)
    response = await client.put(
        f"/api/v1/users/1/alerts/{alert_id}/notifications/99999",
        json={"title": "Ghost"},
        headers=gestor_headers,
    )
    assert response.status_code == 404


async def test_delete_notification(client, gestor_headers):
    alert_id = await _create_alert(client, gestor_headers)
    now = "2025-01-01T00:00:00Z"
    create_resp = await client.post(
        f"/api/v1/users/1/alerts/{alert_id}/notifications",
        json={"timestamp": now, "title": "ToDelete"},
        headers=gestor_headers,
    )
    notif_id = create_resp.json()["id"]

    response = await client.delete(
        f"/api/v1/users/1/alerts/{alert_id}/notifications/{notif_id}",
        headers=gestor_headers,
    )
    assert response.status_code == 204

    get_resp = await client.get(
        f"/api/v1/users/1/alerts/{alert_id}/notifications/{notif_id}",
        headers=gestor_headers,
    )
    assert get_resp.status_code == 404


async def test_delete_notification_not_found(client, gestor_headers):
    alert_id = await _create_alert(client, gestor_headers)
    response = await client.delete(
        f"/api/v1/users/1/alerts/{alert_id}/notifications/99999",
        headers=gestor_headers,
    )
    assert response.status_code == 404
