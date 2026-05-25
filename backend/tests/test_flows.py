from uuid import uuid4
import pytest

pytestmark = pytest.mark.usefixtures("clean_alerts")


async def test_flujo_completo_gestion_noticias(client, gestor_headers):
    """
    Simula el flujo completo de un Gestor:
    1. Login -> 2. Crear Canal RSS -> 3. Crear Alerta de término
    """
    suffix = uuid4().hex[:8]
    canal_data = {
        "name": f"TestSource-{suffix}",
        "url": f"https://test-source-{suffix}.com/rss",
    }
    res_canal = await client.post("/api/v1/information-sources", json=canal_data, headers=gestor_headers)

    suffix2 = uuid4().hex[:8]
    alerta_data = {
        "name": f"AlertaIA-{suffix2}",
        "cron_expression": "0 0 * * *",
        "descriptors": [f"tag-{suffix2}"],
    }
    res_alerta = await client.post("/api/v1/users/1/alerts", json=alerta_data, headers=gestor_headers)

    assert res_canal.status_code == 201
    assert res_alerta.status_code == 201


async def test_flujo_baja_de_terminos(client, gestor_headers):
    """Valida que un usuario puede dejar de seguir un término (borrar alerta)"""
    suffix = uuid4().hex[:8]
    alerta_data = {
        "name": f"AlertaBorrar-{suffix}",
        "cron_expression": "0 0 * * *",
        "descriptors": [f"tag-{suffix}"],
    }
    res_crear = await client.post("/api/v1/users/1/alerts", json=alerta_data, headers=gestor_headers)

    alerta_id = res_crear.json()["id"]
    response = await client.delete(f"/api/v1/users/1/alerts/{alerta_id}", headers=gestor_headers)
    assert response.status_code == 204
