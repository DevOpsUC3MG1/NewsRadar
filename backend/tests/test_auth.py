# backend/tests/test_auth.py

def test_auth_01_registro_exitoso(client, db_engine):
    """Prueba que un usuario nuevo puede registrarse correctamente"""
    
    # 1. Preparamos los datos
    payload = {
        "username": "nuevo_tester",
        "email": "tester@newsradar.es",
        "password": "Password123!"
    }
    
    # 2. Hacemos la petición (simulando al Frontend)
    response = client.post("/api/v1/auth/register", json=payload)
    
    # 3. Verificamos el resultado
    assert response.status_code == 201
    assert response.json()["email"] == "tester@newsradar.es"
    # IMPORTANTE: Nunca debe devolver la contraseña en texto plano
    assert "password" not in response.json()

def test_auth_02_email_duplicado(client):
    """Prueba que no se pueden registrar dos usuarios con el mismo email"""
    
    payload = {
        "username": "copion",
        "email": "tester@newsradar.es", # Este email ya se usó en el test anterior
        "password": "Password123!"
    }
    
    # Insertamos la primera vez
    client.post("/api/v1/auth/register", json=payload)
    
    # Intentamos insertar la segunda vez
    response_duplicado = client.post("/api/v1/auth/register", json=payload)
    
    # Verificamos que el sistema lo rechaza
    assert response_duplicado.status_code == 400

    def test_login_exitoso(client, load_valid_users):
    # 1. Obtenemos los datos del JSON
    datos_admin = load_valid_users["gestor_admin"]
    
    # 2. Hacemos la petición de Login
    response = client.post(
        "/api/v1/auth/login", 
        json={"email": datos_admin["email"], "password": datos_admin["password"]}
    )
    
    # 3. Comprobamos que devuelve un Token
    assert response.status_code == 200
    assert "access_token" in response.json()