async def test_list_roles(client, gestor_headers):
    response = await client.get("/api/v1/roles", headers=gestor_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    names = [r["name"] for r in data]
    assert "admin" in names
    assert "user" in names


async def test_get_role(client, gestor_headers):
    response = await client.get("/api/v1/roles/1", headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "admin"


async def test_get_role_not_found(client, gestor_headers):
    response = await client.get("/api/v1/roles/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_create_role(client, gestor_headers):
    payload = {"name": "editor"}
    response = await client.post("/api/v1/roles", json=payload, headers=gestor_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "editor"


async def test_update_role(client, gestor_headers):
    payload = {"name": "admin-updated"}
    response = await client.put("/api/v1/roles/1", json=payload, headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "admin-updated"


async def test_update_role_not_found(client, gestor_headers):
    payload = {"name": "ghost"}
    response = await client.put("/api/v1/roles/99999", json=payload, headers=gestor_headers)
    assert response.status_code == 404


async def test_delete_role(client, gestor_headers):
    create_resp = await client.post("/api/v1/roles", json={"name": "temporary"}, headers=gestor_headers)
    role_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/roles/{role_id}", headers=gestor_headers)
    assert response.status_code == 204

    get_resp = await client.get(f"/api/v1/roles/{role_id}", headers=gestor_headers)
    assert get_resp.status_code == 404


async def test_delete_role_not_found(client, gestor_headers):
    response = await client.delete("/api/v1/roles/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_create_role_empty_name(client, gestor_headers):
    payload = {"name": ""}
    response = await client.post("/api/v1/roles", json=payload, headers=gestor_headers)
    assert response.status_code == 422
