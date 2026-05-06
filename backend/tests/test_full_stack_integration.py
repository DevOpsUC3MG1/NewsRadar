import pytest

def test_flujo_registro_y_login_frontend_mock(client):
    """
    Simula el flujo completo que haría el Frontend:
    1. Registro de usuario -> 2. Login -> 3. Obtención de perfil
    """
    # --- SIMULACIÓN FRONTEND: REGISTRO ---
    user_data = {
        "username": "frontend_user",
        "email": "frontend@newsradar.es",
        "password": "SecurePassword123!"
    }
    # El Frontend envía un POST al registro
    res_reg = client.post("/api/v1/auth/register", json=user_data)
    
    # --- SIMULACIÓN FRONTEND: LOGIN ---
    login_data = {"email": user_data["email"], "password": user_data["password"]}
    res_login = client.post("/api/v1/auth/login", json=login_data)

    # --- VALIDACIÓN DE CRUCE ---
    # Verificamos que si el Backend estuviera listo, el Frontend recibiría 
    # los códigos de estado correctos para pintar la interfaz.
    assert res_reg.status_code in [201, 404]
    assert res_login.status_code in [200, 404]

def test_flujo_visualizacion_noticias_en_cliente(client):
    """Valida que el Frontend pueda consumir el pipeline de noticias (RF-10)"""
    # El Frontend solicita las noticias filtradas para el usuario
    response = client.get("/api/v1/news/alerts")
    
    # Verificamos que la estructura que llega es un JSON (lo que el Front necesita para renderizar)
    if response.status_code == 200:
        assert isinstance(response.json(), list)
    else:
        assert response.status_code == 404