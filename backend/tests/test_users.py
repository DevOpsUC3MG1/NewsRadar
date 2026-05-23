async def test_list_users(client, gestor_headers):
    response = await client.get("/api/v1/users", headers=gestor_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(u["email"] == "admin@newsradar.com" for u in data)


async def test_get_user(client, gestor_headers):
    response = await client.get("/api/v1/users/1", headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "admin@newsradar.com"


async def test_get_user_not_found(client, gestor_headers):
    response = await client.get("/api/v1/users/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_create_user(client, gestor_headers):
    payload = {
        "email": "newuser@newsradar.es",
        "password": "NewUser123!",
        "first_name": "New",
        "last_name": "User",
        "organization": "NewsRadar",
        "role_ids": [],
    }
    response = await client.post("/api/v1/users", json=payload, headers=gestor_headers)
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@newsradar.es"
    assert "password" not in response.json()


async def test_update_user(client, gestor_headers):
    payload = {
        "first_name": "Updated",
        "last_name": "Name",
    }
    response = await client.put("/api/v1/users/1", json=payload, headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"


async def test_update_user_not_found(client, gestor_headers):
    payload = {"first_name": "Nope"}
    response = await client.put("/api/v1/users/99999", json=payload, headers=gestor_headers)
    assert response.status_code == 404


async def test_delete_user(client, gestor_headers):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "delete_me@newsradar.es",
        "password": "Delete123!",
        "first_name": "Delete",
        "last_name": "Me",
        "organization": "NewsRadar",
    })
    user_id = resp.json()["id"]

    response = await client.delete(f"/api/v1/users/{user_id}", headers=gestor_headers)
    assert response.status_code == 204

    get_resp = await client.get(f"/api/v1/users/{user_id}", headers=gestor_headers)
    assert get_resp.status_code == 404


async def test_delete_user_not_found(client, gestor_headers):
    response = await client.delete("/api/v1/users/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_create_user_invalid_role_id(client, gestor_headers):
    payload = {
        "email": "badrole@newsradar.es",
        "password": "BadRole123!",
        "first_name": "Bad",
        "last_name": "Role",
        "organization": "NewsRadar",
        "role_ids": [99999],
    }
    response = await client.post("/api/v1/users", json=payload, headers=gestor_headers)
    assert response.status_code == 400
