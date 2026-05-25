import os
import pytest
from uuid import uuid4


async def test_auth_01_registro_exitoso(client):
    """Prueba que un usuario nuevo puede registrarse correctamente"""
    suffix = uuid4().hex[:8]
    email = f"tester-{suffix}@newsradar.es"
    payload = {
        "email": email,
        "password": "Password123!",
        "first_name": "Nuevo",
        "last_name": "Tester",
        "organization": "NewsRadar",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    assert response.json()["email"] == email
    assert "password" not in response.json()


async def test_auth_02_email_duplicado(client):
    """Prueba que no se pueden registrar dos usuarios con el mismo email"""
    suffix = uuid4().hex[:8]
    email = f"duplicado-{suffix}@newsradar.es"
    payload = {
        "email": email,
        "password": "Password123!",
        "first_name": "Test",
        "last_name": "User",
        "organization": "NewsRadar",
    }
    resp1 = await client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 200

    resp2 = await client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == 409


async def test_login_exitoso(client):
    """Prueba que un usuario registrado puede hacer login"""
    response = await client.post("/api/v1/auth/login", json={
        "email": "admin@newsradar.com",
        "password": "admin123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_verify_account_invalid_token(client):
    response = await client.post("/api/v1/auth/verify", json={"token": "invalid-token-123"})
    assert response.status_code == 404


async def test_verify_account_already_verified(client):
    response = await client.post("/api/v1/auth/verify", json={"token": "any-token"})
    assert response.status_code in (404, 400)


async def test_resend_verification_email_not_found(client):
    response = await client.post("/api/v1/auth/resend-verification?payload=ghost@test.com")
    assert response.status_code == 404


async def test_forgot_password_unknown_email(client):
    response = await client.post("/api/v1/auth/forgot-password", json={"email": "nonexistent@test.com"})
    assert response.status_code == 200


async def test_forgot_password_known_email(client):
    response = await client.post("/api/v1/auth/forgot-password", json={"email": "admin@newsradar.com"})
    assert response.status_code == 200


async def test_reset_password_invalid_token(client):
    response = await client.post("/api/v1/auth/reset-password", json={
        "token": "bad-token",
        "new_password": "NewPass123!",
    })
    assert response.status_code == 400


@pytest.fixture
def mock_rss_xml():
    """Lee el archivo XML falso para simular una respuesta de un feed RSS"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    xml_path = os.path.join(base_dir, "fixtures", "feed_falso.xml")
    with open(xml_path, "r", encoding="utf-8") as file:
        return file.read()
