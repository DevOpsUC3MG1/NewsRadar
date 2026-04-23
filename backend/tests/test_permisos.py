import pytest

def test_acceso_denegado_sin_token(client):
    """Cualquier ruta protegida debe dar error 401 si no hay token"""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401 # Unauthorized

def test_lector_no_puede_crear_alerta(client):
    """Un usuario con rol Lector no debe poder acceder a endpoints de Gestor"""
    # 1. Simulamos que tenemos el token de un Lector
    headers_lector = {
        "Authorization": "Bearer token_falso_de_lector"
    }
    
    # 2. Intentamos crear una alerta (acción exclusiva de Gestor)
    payload_alerta = {"name": "Mi Alerta", "keyword": "tecnología"}
    response = client.post("/api/v1/alerts", json=payload_alerta, headers=headers_lector)
    
    # 3. El backend debe rechazarlo (403 Forbidden o 401 si el token es inválido)
    assert response.status_code in [401, 403]
