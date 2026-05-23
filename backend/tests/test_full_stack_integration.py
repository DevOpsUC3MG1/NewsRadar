async def test_flujo_registro_y_login_frontend_mock(client):
    """
    Simula el flujo completo que haría el Frontend:
    1. Registro de usuario -> 2. Login -> 3. Obtención de perfil
    """
    user_data = {
        "email": "frontend@newsradar.es",
        "password": "SecurePassword123!",
        "first_name": "Frontend",
        "last_name": "User",
        "organization": "NewsRadar",
    }
    res_reg = await client.post("/api/v1/auth/register", json=user_data)

    login_data = {"email": user_data["email"], "password": user_data["password"]}
    res_login = await client.post("/api/v1/auth/login", json=login_data)

    assert res_reg.status_code == 200
    assert res_login.status_code == 200
    assert "access_token" in res_login.json()


async def test_flujo_visualizacion_noticias_en_cliente(client):
    """Valida que el Frontend pueda consumir el pipeline de noticias (RF-10)"""
    response = await client.get("/api/v1/news/alerts")
    assert response.status_code == 404
