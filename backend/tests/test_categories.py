VALID_CAT = "Ciencia y tecnología"


async def test_list_categories(client, gestor_headers):
    response = await client.get("/api/v1/categories", headers=gestor_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


async def test_create_category(client, gestor_headers):
    payload = {"name": VALID_CAT, "source": "IPTC"}
    response = await client.post("/api/v1/categories", json=payload, headers=gestor_headers)
    assert response.status_code == 201
    assert response.json()["name"] == VALID_CAT


async def test_get_category(client, gestor_headers):
    create_resp = await client.post("/api/v1/categories", json={"name": "Deporte", "source": "IPTC"}, headers=gestor_headers)
    cat_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/categories/{cat_id}", headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Deporte"


async def test_get_category_not_found(client, gestor_headers):
    response = await client.get("/api/v1/categories/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_update_category(client, gestor_headers):
    create_resp = await client.post("/api/v1/categories", json={"name": "Política", "source": "IPTC"}, headers=gestor_headers)
    cat_id = create_resp.json()["id"]

    response = await client.put(f"/api/v1/categories/{cat_id}", json={"name": "Política y gobierno"}, headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Política y gobierno"


async def test_update_category_not_found(client, gestor_headers):
    response = await client.put("/api/v1/categories/99999", json={"name": VALID_CAT}, headers=gestor_headers)
    assert response.status_code == 404


async def test_delete_category(client, gestor_headers):
    create_resp = await client.post("/api/v1/categories", json={"name": "Salud", "source": "IPTC"}, headers=gestor_headers)
    cat_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/categories/{cat_id}", headers=gestor_headers)
    assert response.status_code == 204

    get_resp = await client.get(f"/api/v1/categories/{cat_id}", headers=gestor_headers)
    assert get_resp.status_code == 404


async def test_delete_category_not_found(client, gestor_headers):
    response = await client.delete("/api/v1/categories/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_create_category_invalid_name(client, gestor_headers):
    payload = {"name": "NotInIPTC", "source": "IPTC"}
    response = await client.post("/api/v1/categories", json=payload, headers=gestor_headers)
    assert response.status_code == 422
