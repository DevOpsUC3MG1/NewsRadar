async def test_acceso_denegado_sin_token(client):
    """Cualquier ruta protegida debe dar error 401 si no hay token"""
    response = await client.get("/api/v1/users/1")
    assert response.status_code == 401


async def test_lector_no_puede_crear_alerta(client):
    """Un usuario sin rol de gestor no debe poder crear alertas"""
    payload_alerta = {"name": "Mi Alerta", "cron_expression": "0 0 * * *"}
    response = await client.post("/api/v1/users/1/alerts", json=payload_alerta)
    assert response.status_code == 401
