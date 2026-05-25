async def test_list_information_sources(client, gestor_headers):
    response = await client.get("/api/v1/information-sources", headers=gestor_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


from uuid import uuid4


async def test_create_information_source(client, gestor_headers):
    suffix = uuid4().hex[:8]
    name = f"TestSource-{suffix}"
    url = f"https://test-source-{suffix}.com"
    payload = {"name": name, "url": url}
    response = await client.post("/api/v1/information-sources", json=payload, headers=gestor_headers)
    assert response.status_code == 201
    assert response.json()["name"] == name


async def test_get_information_source(client, gestor_headers):
    suffix = uuid4().hex[:8]
    name = f"GetSource-{suffix}"
    url = f"https://get-source-{suffix}.com"
    create_resp = await client.post("/api/v1/information-sources", json={"name": name, "url": url}, headers=gestor_headers)
    source_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/information-sources/{source_id}", headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["name"] == name


async def test_get_information_source_not_found(client, gestor_headers):
    response = await client.get("/api/v1/information-sources/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_update_information_source(client, gestor_headers):
    suffix = uuid4().hex[:8]
    name = f"UpdSrc-{suffix}"
    url = f"https://upd-src-{suffix}.com"
    create_resp = await client.post("/api/v1/information-sources", json={"name": name, "url": url}, headers=gestor_headers)
    source_id = create_resp.json()["id"]

    new_name = f"UpdSrcRenamed-{suffix}"
    response = await client.put(f"/api/v1/information-sources/{source_id}", json={"name": new_name}, headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["name"] == new_name


async def test_update_information_source_not_found(client, gestor_headers):
    response = await client.put("/api/v1/information-sources/99999", json={"name": "Ghost"}, headers=gestor_headers)
    assert response.status_code == 404


async def test_delete_information_source(client, gestor_headers):
    suffix = uuid4().hex[:8]
    name = f"DelSrc-{suffix}"
    url = f"https://del-src-{suffix}.com"
    create_resp = await client.post("/api/v1/information-sources", json={"name": name, "url": url}, headers=gestor_headers)
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
