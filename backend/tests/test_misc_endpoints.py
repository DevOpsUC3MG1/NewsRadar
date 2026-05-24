"""Tests for dashboard, wordcloud, and misc endpoints"""


async def test_dashboard(client, gestor_headers):
    response = await client.get("/api/v1/dashboard", headers=gestor_headers)
    assert response.status_code == 200
    data = response.json()
    assert "fuentes" in data
    assert "noticias" in data
    assert "alertas" in data
    assert "evolucion" in data
    assert "categorias" in data


async def test_wordcloud_global(client, gestor_headers):
    response = await client.get("/api/v1/resumen/clouds/global", headers=gestor_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_wordcloud_by_category(client, gestor_headers):
    response = await client.get("/api/v1/resumen/clouds/economy", headers=gestor_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_suggest_synonyms(client, gestor_headers):
    payload = {"keywords": ["tecnología"], "max_synonyms": 3}
    response = await client.post("/api/v1/alerts/suggest-synonyms", json=payload, headers=gestor_headers)
    assert response.status_code == 200
    data = response.json()
    assert "keywords" in data
    assert "suggested_synonyms" in data
