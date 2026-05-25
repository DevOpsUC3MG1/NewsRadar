from uuid import uuid4


async def test_list_roles(client, gestor_headers):
    response = await client.get("/api/v1/roles", headers=gestor_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


async def test_get_role(client, gestor_headers):
    response = await client.get("/api/v1/roles/1", headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["id"] == 1


async def test_get_role_not_found(client, gestor_headers):
    response = await client.get("/api/v1/roles/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_create_role(client, gestor_headers):
    suffix = uuid4().hex[:8]
    payload = {"name": f"role-{suffix}"}
    response = await client.post("/api/v1/roles", json=payload, headers=gestor_headers)
    assert response.status_code == 201
    assert response.json()["name"] == f"role-{suffix}"


async def test_update_role(client, gestor_headers):
    # Create a fresh role so we don't mutate seeded data
    suffix = uuid4().hex[:8]
    create_resp = await client.post("/api/v1/roles", json={"name": f"role-{suffix}"}, headers=gestor_headers)
    role_id = create_resp.json()["id"]
    new_name = f"role-updated-{suffix}"

    response = await client.put(f"/api/v1/roles/{role_id}", json={"name": new_name}, headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["name"] == new_name


async def test_update_role_not_found(client, gestor_headers):
    payload = {"name": "ghost"}
    response = await client.put("/api/v1/roles/99999", json=payload, headers=gestor_headers)
    assert response.status_code == 404


async def test_delete_role(client, gestor_headers):
    suffix = uuid4().hex[:8]
    create_resp = await client.post("/api/v1/roles", json={"name": f"role-{suffix}"}, headers=gestor_headers)
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
