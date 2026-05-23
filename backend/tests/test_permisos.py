def test_acceso_denegado_sin_token(client):
    """Cualquier ruta protegida debe dar error 401 si no hay token"""
    response = client.get("/api/v1/users/1")
    assert response.status_code == 401


def test_lector_no_puede_crear_alerta(client):
    """Un usuario con rol Lector no debe poder acceder a endpoints de Gestor"""
    headers_lector = {
        "Authorization": "Bearer token_falso_de_lector"
    }

    payload_alerta = {"name": "Mi Alerta", "cron_expression": "0 0 * * *"}
    response = client.post("/api/v1/users/1/alerts", json=payload_alerta, headers=headers_lector)

    assert response.status_code in [401, 403]
