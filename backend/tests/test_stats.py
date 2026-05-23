"""Tests for Stats CRUD — MongoDB-backed"""


async def test_create_stats(client, gestor_headers):
    payload = {"metrics": [{"name": "articles", "value": 42}]}
    response = await client.post("/api/v1/stats", json=payload, headers=gestor_headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["metrics"][0]["name"] == "articles"
    assert data["metrics"][0]["value"] == 42


async def test_list_stats(client, gestor_headers):
    payload = {"metrics": [{"name": "visitors", "value": 100}]}
    await client.post("/api/v1/stats", json=payload, headers=gestor_headers)

    response = await client.get("/api/v1/stats", headers=gestor_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_get_stats(client, gestor_headers):
    create_resp = await client.post("/api/v1/stats", json={"metrics": [{"name": "cpu", "value": 75}]}, headers=gestor_headers)
    stats_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/stats/{stats_id}", headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["metrics"][0]["name"] == "cpu"


async def test_get_stats_not_found(client, gestor_headers):
    response = await client.get("/api/v1/stats/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_update_stats(client, gestor_headers):
    create_resp = await client.post("/api/v1/stats", json={"metrics": [{"name": "old", "value": 1}]}, headers=gestor_headers)
    stats_id = create_resp.json()["id"]

    response = await client.put(f"/api/v1/stats/{stats_id}", json={"metrics": [{"name": "new", "value": 2}]}, headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["metrics"][0]["name"] == "new"


async def test_update_stats_not_found(client, gestor_headers):
    response = await client.put("/api/v1/stats/99999", json={"metrics": [{"name": "ghost", "value": 0}]}, headers=gestor_headers)
    assert response.status_code == 404


async def test_delete_stats(client, gestor_headers):
    create_resp = await client.post("/api/v1/stats", json={"metrics": [{"name": "temp", "value": 0}]}, headers=gestor_headers)
    stats_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/stats/{stats_id}", headers=gestor_headers)
    assert response.status_code == 204

    get_resp = await client.get(f"/api/v1/stats/{stats_id}", headers=gestor_headers)
    assert get_resp.status_code == 404


async def test_delete_stats_not_found(client, gestor_headers):
    response = await client.delete("/api/v1/stats/99999", headers=gestor_headers)
    assert response.status_code == 404
