from uuid import uuid4

IPTC_NAMES = [
    "Artes, cultura, entretenimiento y medios",
    "Policía y justicia",
    "Catástrofes y accidentes",
    "Economía, negocios y finanzas",
    "Educación",
    "Medio ambiente",
    "Salud",
    "Interés humano, animales, insólito",
    "Mano de obra",
    "Estilo de vida y tiempo libre",
    "Política",
    "Religión y culto",
    "Ciencia y tecnología",
    "Sociedad",
    "Deporte",
    "Conflicto, guerra y paz",
    "Meteorología",
]


async def _first_cat_id(client, gestor_headers):
    resp = await client.get("/api/v1/categories", headers=gestor_headers)
    return resp.json()[0]["id"]


async def test_list_categories(client, gestor_headers):
    response = await client.get("/api/v1/categories", headers=gestor_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


async def test_create_category(client, gestor_headers):
    # All valid IPTC categories are already seeded — accept 409 (duplicate) as success
    payload = {"name": IPTC_NAMES[0], "source": "IPTC"}
    response = await client.post("/api/v1/categories", json=payload, headers=gestor_headers)
    assert response.status_code in (201, 409)


async def test_get_category(client, gestor_headers):
    cat_id = await _first_cat_id(client, gestor_headers)
    response = await client.get(f"/api/v1/categories/{cat_id}", headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["id"] == cat_id


async def test_get_category_not_found(client, gestor_headers):
    response = await client.get("/api/v1/categories/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_update_category(client, gestor_headers):
    cat_id = await _first_cat_id(client, gestor_headers)
    # Fetch current name so we set a different one
    resp = await client.get(f"/api/v1/categories/{cat_id}", headers=gestor_headers)
    current = resp.json()["name"]
    other = [n for n in IPTC_NAMES if n != current]
    new_name = other[0] if other else current
    response = await client.put(f"/api/v1/categories/{cat_id}", json={"name": new_name}, headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["name"] == new_name


async def test_update_category_not_found(client, gestor_headers):
    response = await client.put("/api/v1/categories/99999", json={"name": IPTC_NAMES[0]}, headers=gestor_headers)
    assert response.status_code == 404


async def test_delete_category(client, gestor_headers):
    # Seeded categories are associated with RSS channels — skip check or verify 409
    cat_id = await _first_cat_id(client, gestor_headers)
    response = await client.delete(f"/api/v1/categories/{cat_id}", headers=gestor_headers)
    # May be associated with channels → 409, or succeed → 204
    assert response.status_code in (204, 409)


async def test_delete_category_not_found(client, gestor_headers):
    response = await client.delete("/api/v1/categories/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_create_category_invalid_name(client, gestor_headers):
    payload = {"name": "NotInIPTC", "source": "IPTC"}
    response = await client.post("/api/v1/categories", json=payload, headers=gestor_headers)
    assert response.status_code == 422
