async def test_list_information_sources(client, gestor_headers):
    response = await client.get("/api/v1/information-sources", headers=gestor_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


async def test_create_information_source(client, gestor_headers):
    payload = {"name": "El País", "url": "https://elpais.com"}
    response = await client.post("/api/v1/information-sources", json=payload, headers=gestor_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "El País"


async def test_get_information_source(client, gestor_headers):
    create_resp = await client.post("/api/v1/information-sources", json={"name": "Marca", "url": "https://marca.com"}, headers=gestor_headers)
    source_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/information-sources/{source_id}", headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Marca"


async def test_get_information_source_not_found(client, gestor_headers):
    response = await client.get("/api/v1/information-sources/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_update_information_source(client, gestor_headers):
    create_resp = await client.post("/api/v1/information-sources", json={"name": "ABC", "url": "https://abc.es"}, headers=gestor_headers)
    source_id = create_resp.json()["id"]

    response = await client.put(f"/api/v1/information-sources/{source_id}", json={"name": "ABC Actualizado"}, headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "ABC Actualizado"


async def test_update_information_source_not_found(client, gestor_headers):
    response = await client.put("/api/v1/information-sources/99999", json={"name": "Ghost"}, headers=gestor_headers)
    assert response.status_code == 404


async def test_delete_information_source(client, gestor_headers):
    create_resp = await client.post("/api/v1/information-sources", json={"name": "TempSource", "url": "https://temp.com"}, headers=gestor_headers)
    source_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/information-sources/{source_id}", headers=gestor_headers)
    assert response.status_code == 204

    get_resp = await client.get(f"/api/v1/information-sources/{source_id}", headers=gestor_headers)
    assert get_resp.status_code == 404


async def test_delete_information_source_not_found(client, gestor_headers):
    response = await client.delete("/api/v1/information-sources/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_create_information_source_invalid_url(client, gestor_headers):
    payload = {"name": "Bad", "url": "not-a-url"}
    response = await client.post("/api/v1/information-sources", json=payload, headers=gestor_headers)
    assert response.status_code == 422
