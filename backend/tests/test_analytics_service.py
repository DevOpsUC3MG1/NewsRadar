"""Tests for analytics_service — uses real DB and MongoDB"""


async def test_build_wordcloud_global_via_api(client, gestor_headers):
    response = await client.get("/api/v1/resumen/clouds/global?days=30&limit=5", headers=gestor_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_build_wordcloud_by_category_via_api(client, gestor_headers):
    response = await client.get("/api/v1/resumen/clouds/economy?days=30&limit=5", headers=gestor_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_build_dashboard_no_mongo_data(client, gestor_headers):
    response = await client.get("/api/v1/dashboard?days=7", headers=gestor_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["fuentes"]["activas"] >= 0
    assert isinstance(data["categorias"], list)
