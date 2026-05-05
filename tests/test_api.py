"""
Pruebas funcionales del API REST de NewsRadar.
Cubre todos los endpoints del Anexo I con casos positivos y negativos.

Uso:
    pip install requests pytest
    pytest test_api.py -v

Requisitos:
    - La API debe estar corriendo en BASE_URL (por defecto http://localhost:8000)
    - Las credenciales seed deben existir: admin@newsradar.com / admin123
"""

import requests
import pytest
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000/api/v1"

ADMIN_EMAIL    = "admin@newsradar.com"
ADMIN_PASSWORD = "admin123"

# ─────────────────────────────────────────────
# FIXTURES / HELPERS
# ─────────────────────────────────────────────

def login(email=ADMIN_EMAIL, password=ADMIN_PASSWORD) -> str:
    """Devuelve el access_token para el usuario dado."""
    r = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, f"Login fallido: {r.text}"
    return r.json()["access_token"]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# Token global reutilizado en todos los tests que necesitan autenticación
@pytest.fixture(scope="session")
def token() -> str:
    return login()


@pytest.fixture(scope="session")
def headers(token) -> dict:
    return auth(token)


# ─────────────────────────────────────────────
# SYSTEM
# ─────────────────────────────────────────────

class TestHealth:
    def test_health_ok(self):
        r = requests.get(f"{BASE_URL}/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert "timestamp" in body


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

class TestLogin:
    def test_login_ok(self):
        r = requests.post(f"{BASE_URL}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
        })
        assert r.status_code == 200
        body = r.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_login_wrong_password(self):
        r = requests.post(f"{BASE_URL}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": "contraseña_incorrecta",
        })
        assert r.status_code == 401

    def test_login_unknown_email(self):
        r = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "noexiste@example.com",
            "password": "cualquiera",
        })
        assert r.status_code == 401

    def test_login_missing_fields(self):
        r = requests.post(f"{BASE_URL}/auth/login", json={"email": ADMIN_EMAIL})
        assert r.status_code == 422

    def test_login_invalid_email_format(self):
        r = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "no-es-un-email",
            "password": "admin123",
        })
        assert r.status_code == 422


class TestRegister:
    UNIQUE_EMAIL = f"test_register_{datetime.now().timestamp()}@example.com"

    def test_register_ok(self, headers):
        # Obtenemos un role_id válido primero
        roles = requests.get(f"{BASE_URL}/roles", headers=headers).json()
        role_id = roles[0]["id"] if roles else []

        r = requests.post(f"{BASE_URL}/auth/register", json={
            "email": self.UNIQUE_EMAIL,
            "first_name": "Test",
            "last_name": "Register",
            "organization": "UC3M",
            "password": "password123",
            "role_ids": [role_id] if role_id else [],
        })
        assert r.status_code == 200
        body = r.json()
        assert body["email"] == self.UNIQUE_EMAIL
        assert "password" not in body  # no se expone el hash

    def test_register_duplicate_email(self, headers):
        roles = requests.get(f"{BASE_URL}/roles", headers=headers).json()
        role_id = roles[0]["id"] if roles else []

        payload = {
            "email": self.UNIQUE_EMAIL,
            "first_name": "Dup",
            "last_name": "User",
            "organization": "UC3M",
            "password": "password123",
            "role_ids": [role_id] if role_id else [],
        }
        # Primer registro puede fallar si ya existe del test anterior — no pasa nada
        requests.post(f"{BASE_URL}/auth/register", json=payload)
        # El segundo DEBE fallar con 409
        r = requests.post(f"{BASE_URL}/auth/register", json=payload)
        assert r.status_code == 409

    def test_register_invalid_role(self):
        r = requests.post(f"{BASE_URL}/auth/register", json={
            "email": f"role_invalid_{datetime.now().timestamp()}@example.com",
            "first_name": "Bad",
            "last_name": "Role",
            "organization": "UC3M",
            "password": "password123",
            "role_ids": [99999],
        })
        assert r.status_code == 400

    def test_register_password_too_short(self):
        r = requests.post(f"{BASE_URL}/auth/register", json={
            "email": f"short_{datetime.now().timestamp()}@example.com",
            "first_name": "Short",
            "last_name": "Pass",
            "organization": "UC3M",
            "password": "12345",  # menos de 6 caracteres
            "role_ids": [],
        })
        assert r.status_code == 422

    def test_register_missing_required_fields(self):
        r = requests.post(f"{BASE_URL}/auth/register", json={
            "email": "missing@example.com",
            "password": "password123",
        })
        assert r.status_code == 422


class TestVerifyAccount:
    def test_verify_invalid_token(self):
        r = requests.post(f"{BASE_URL}/auth/verify", json={"token": "token-que-no-existe"})
        assert r.status_code == 404

    def test_verify_missing_token(self):
        r = requests.post(f"{BASE_URL}/auth/verify", json={})
        assert r.status_code == 422


class TestForgotPassword:
    def test_forgot_password_registered_email(self):
        # Siempre devuelve 200 por seguridad (no revela si el email existe)
        r = requests.post(f"{BASE_URL}/auth/forgot-password", json={"email": ADMIN_EMAIL})
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_forgot_password_unknown_email(self):
        r = requests.post(f"{BASE_URL}/auth/forgot-password", json={"email": "noexiste@example.com"})
        assert r.status_code == 200  # respuesta genérica deliberada
        assert r.json()["success"] is True

    def test_forgot_password_invalid_email(self):
        r = requests.post(f"{BASE_URL}/auth/forgot-password", json={"email": "no-es-email"})
        assert r.status_code == 422


class TestResetPassword:
    def test_reset_password_invalid_token(self):
        r = requests.post(f"{BASE_URL}/auth/reset-password", json={
            "token": "token-falso",
            "new_password": "nuevapassword123",
        })
        assert r.status_code == 400

    def test_reset_password_short_password(self):
        r = requests.post(f"{BASE_URL}/auth/reset-password", json={
            "token": "cualquiera",
            "new_password": "123",
        })
        assert r.status_code == 422

    def test_reset_password_missing_fields(self):
        r = requests.post(f"{BASE_URL}/auth/reset-password", json={"token": "tok"})
        assert r.status_code == 422


class TestProtectedEndpointsAuth:
    """Verificar que todos los endpoints protegidos rechazan requests sin token."""

    def test_no_token_list_users(self):
        r = requests.get(f"{BASE_URL}/users")
        assert r.status_code in (401, 403)

    def test_invalid_token_list_users(self):
        r = requests.get(f"{BASE_URL}/users", headers={"Authorization": "Bearer token-invalido"})
        assert r.status_code == 401

    def test_no_token_list_roles(self):
        r = requests.get(f"{BASE_URL}/roles")
        assert r.status_code in (401, 403)

    def test_no_token_list_categories(self):
        r = requests.get(f"{BASE_URL}/categories")
        assert r.status_code in (401, 403)

    def test_no_token_list_sources(self):
        r = requests.get(f"{BASE_URL}/information-sources")
        assert r.status_code in (401, 403)


# ─────────────────────────────────────────────
# ROLES
# ─────────────────────────────────────────────

class TestRoles:
    @pytest.fixture(autouse=True)
    def setup(self, headers):
        self.h = headers

    def test_list_roles(self):
        r = requests.get(f"{BASE_URL}/roles", headers=self.h)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_role(self):
        name = f"role_test_{datetime.now().timestamp()}"
        r = requests.post(f"{BASE_URL}/roles", headers=self.h, json={"name": name})
        assert r.status_code == 201
        body = r.json()
        assert body["name"] == name
        assert "id" in body
        return body["id"]

    def test_get_role_ok(self):
        # Crear primero
        name = f"get_role_{datetime.now().timestamp()}"
        created = requests.post(f"{BASE_URL}/roles", headers=self.h, json={"name": name}).json()
        role_id = created["id"]

        r = requests.get(f"{BASE_URL}/roles/{role_id}", headers=self.h)
        assert r.status_code == 200
        assert r.json()["id"] == role_id

    def test_get_role_not_found(self):
        r = requests.get(f"{BASE_URL}/roles/999999", headers=self.h)
        assert r.status_code == 404

    def test_update_role(self):
        name = f"upd_role_{datetime.now().timestamp()}"
        created = requests.post(f"{BASE_URL}/roles", headers=self.h, json={"name": name}).json()
        role_id = created["id"]

        new_name = f"updated_{datetime.now().timestamp()}"
        r = requests.put(f"{BASE_URL}/roles/{role_id}", headers=self.h, json={"name": new_name})
        assert r.status_code == 200
        assert r.json()["name"] == new_name

    def test_update_role_not_found(self):
        r = requests.put(f"{BASE_URL}/roles/999999", headers=self.h, json={"name": "x"})
        assert r.status_code == 404

    def test_delete_role_ok(self):
        name = f"del_role_{datetime.now().timestamp()}"
        created = requests.post(f"{BASE_URL}/roles", headers=self.h, json={"name": name}).json()
        role_id = created["id"]

        r = requests.delete(f"{BASE_URL}/roles/{role_id}", headers=self.h)
        assert r.status_code == 204

        # Confirmar que ya no existe
        r2 = requests.get(f"{BASE_URL}/roles/{role_id}", headers=self.h)
        assert r2.status_code == 404

    def test_delete_role_not_found(self):
        r = requests.delete(f"{BASE_URL}/roles/999999", headers=self.h)
        assert r.status_code == 404

    def test_delete_role_assigned_to_user(self):
        """No debe poder borrarse un rol asignado a un usuario."""
        # Los roles seed (admin, user) están asignados al usuario admin
        roles = requests.get(f"{BASE_URL}/roles", headers=self.h).json()
        admin_role = next((r for r in roles if r["name"] == "admin"), None)
        if admin_role:
            r = requests.delete(f"{BASE_URL}/roles/{admin_role['id']}", headers=self.h)
            assert r.status_code == 409

    def test_create_role_empty_name(self):
        r = requests.post(f"{BASE_URL}/roles", headers=self.h, json={"name": ""})
        assert r.status_code == 422

    def test_create_role_missing_name(self):
        r = requests.post(f"{BASE_URL}/roles", headers=self.h, json={})
        assert r.status_code == 422


# ─────────────────────────────────────────────
# USERS
# ─────────────────────────────────────────────

class TestUsers:
    @pytest.fixture(autouse=True)
    def setup(self, headers):
        self.h = headers
        roles = requests.get(f"{BASE_URL}/roles", headers=self.h).json()
        self.role_id = roles[0]["id"] if roles else None

    def _create_user(self, suffix=""):
        ts = datetime.now().timestamp()
        return requests.post(f"{BASE_URL}/users", headers=self.h, json={
            "email": f"user_{ts}{suffix}@example.com",
            "first_name": "Test",
            "last_name": "User",
            "organization": "UC3M",
            "password": "password123",
            "role_ids": [self.role_id] if self.role_id else [],
        })

    def test_list_users(self):
        r = requests.get(f"{BASE_URL}/users", headers=self.h)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_user_ok(self):
        r = self._create_user()
        assert r.status_code == 201
        body = r.json()
        assert "id" in body
        assert "password" not in body

    def test_create_user_duplicate_email(self):
        r1 = self._create_user("dup")
        assert r1.status_code == 201
        email = r1.json()["email"]

        r2 = requests.post(f"{BASE_URL}/users", headers=self.h, json={
            "email": email,
            "first_name": "Dup",
            "last_name": "User",
            "organization": "UC3M",
            "password": "password123",
            "role_ids": [],
        })
        assert r2.status_code == 409

    def test_create_user_invalid_role(self):
        r = requests.post(f"{BASE_URL}/users", headers=self.h, json={
            "email": f"badrole_{datetime.now().timestamp()}@example.com",
            "first_name": "Bad",
            "last_name": "Role",
            "organization": "UC3M",
            "password": "password123",
            "role_ids": [99999],
        })
        assert r.status_code == 400

    def test_create_user_missing_fields(self):
        r = requests.post(f"{BASE_URL}/users", headers=self.h, json={"email": "x@x.com"})
        assert r.status_code == 422

    def test_get_user_ok(self):
        created = self._create_user("get").json()
        user_id = created["id"]

        r = requests.get(f"{BASE_URL}/users/{user_id}", headers=self.h)
        assert r.status_code == 200
        assert r.json()["id"] == user_id

    def test_get_user_not_found(self):
        r = requests.get(f"{BASE_URL}/users/999999", headers=self.h)
        assert r.status_code == 404

    def test_update_user_ok(self):
        created = self._create_user("upd").json()
        user_id = created["id"]

        r = requests.put(f"{BASE_URL}/users/{user_id}", headers=self.h, json={
            "first_name": "Updated",
            "organization": "NewOrg",
        })
        assert r.status_code == 200
        assert r.json()["first_name"] == "Updated"

    def test_update_user_duplicate_email(self):
        u1 = self._create_user("em1").json()
        u2 = self._create_user("em2").json()

        r = requests.put(f"{BASE_URL}/users/{u2['id']}", headers=self.h, json={
            "email": u1["email"],
        })
        assert r.status_code == 409

    def test_update_user_not_found(self):
        r = requests.put(f"{BASE_URL}/users/999999", headers=self.h, json={"first_name": "X"})
        assert r.status_code == 404

    def test_delete_user_ok(self):
        created = self._create_user("del").json()
        user_id = created["id"]

        r = requests.delete(f"{BASE_URL}/users/{user_id}", headers=self.h)
        assert r.status_code == 204

        r2 = requests.get(f"{BASE_URL}/users/{user_id}", headers=self.h)
        assert r2.status_code == 404

    def test_delete_user_not_found(self):
        r = requests.delete(f"{BASE_URL}/users/999999", headers=self.h)
        assert r.status_code == 404

    def test_get_verification_status_ok(self):
        r = requests.get(
            f"{BASE_URL}/users/email/{ADMIN_EMAIL}/verification-status",
            headers=self.h,
        )
        assert r.status_code == 200
        body = r.json()
        assert body["email"] == ADMIN_EMAIL
        assert isinstance(body["is_verified"], bool)

    def test_get_verification_status_not_found(self):
        r = requests.get(
            f"{BASE_URL}/users/email/noexiste@example.com/verification-status",
            headers=self.h,
        )
        assert r.status_code == 404


# ─────────────────────────────────────────────
# CATEGORIES
# ─────────────────────────────────────────────

class TestCategories:
    @pytest.fixture(autouse=True)
    def setup(self, headers):
        self.h = headers

    def _create_category(self):
        return requests.post(f"{BASE_URL}/categories", headers=self.h, json={
            "name": f"Cat_{datetime.now().timestamp()}",
            "source": "IPTC",
        })

    def test_list_categories(self):
        r = requests.get(f"{BASE_URL}/categories", headers=self.h)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_category_ok(self):
        r = self._create_category()
        assert r.status_code == 201
        body = r.json()
        assert "id" in body
        assert body["source"] == "IPTC"

    def test_create_category_invalid_source(self):
        """Solo se permite source=IPTC — inspección manual INS-01."""
        r = requests.post(f"{BASE_URL}/categories", headers=self.h, json={
            "name": "Categoria invalida",
            "source": "OTRO",
        })
        assert r.status_code == 422

    def test_create_category_missing_name(self):
        r = requests.post(f"{BASE_URL}/categories", headers=self.h, json={"source": "IPTC"})
        assert r.status_code == 422

    def test_create_category_empty_name(self):
        r = requests.post(f"{BASE_URL}/categories", headers=self.h, json={
            "name": "",
            "source": "IPTC",
        })
        assert r.status_code == 422

    def test_get_category_ok(self):
        created = self._create_category().json()
        r = requests.get(f"{BASE_URL}/categories/{created['id']}", headers=self.h)
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_get_category_not_found(self):
        r = requests.get(f"{BASE_URL}/categories/999999", headers=self.h)
        assert r.status_code == 404

    def test_update_category_ok(self):
        created = self._create_category().json()
        r = requests.put(f"{BASE_URL}/categories/{created['id']}", headers=self.h, json={
            "name": f"Updated_{datetime.now().timestamp()}",
        })
        assert r.status_code == 200

    def test_update_category_invalid_source(self):
        created = self._create_category().json()
        r = requests.put(f"{BASE_URL}/categories/{created['id']}", headers=self.h, json={
            "source": "INVALIDO",
        })
        assert r.status_code == 422

    def test_update_category_not_found(self):
        r = requests.put(f"{BASE_URL}/categories/999999", headers=self.h, json={"name": "X"})
        assert r.status_code == 404

    def test_delete_category_ok(self):
        created = self._create_category().json()
        r = requests.delete(f"{BASE_URL}/categories/{created['id']}", headers=self.h)
        assert r.status_code == 204

        r2 = requests.get(f"{BASE_URL}/categories/{created['id']}", headers=self.h)
        assert r2.status_code == 404

    def test_delete_category_not_found(self):
        r = requests.delete(f"{BASE_URL}/categories/999999", headers=self.h)
        assert r.status_code == 404

    def test_delete_category_in_use(self):
        """No debe poder borrarse si tiene canales RSS asociados."""
        cat = self._create_category().json()
        ts = int(datetime.now().timestamp())
        source = requests.post(f"{BASE_URL}/information-sources", headers=self.h, json={
            "name": f"Src_{ts}",
            "url": f"https://srcinuse{ts}.example.com/rss",
        }).json()
        channel_r = requests.post(
            f"{BASE_URL}/information-sources/{source['id']}/rss-channels",
            headers=self.h,
            json={"url": f"https://feedinuse{ts}.example.com/rss/feed.xml", "category_id": cat["id"]},
        )
        assert channel_r.status_code == 201, f"Canal no creado: {channel_r.text}"
        r = requests.delete(f"{BASE_URL}/categories/{cat['id']}", headers=self.h)
        assert r.status_code == 409


# ─────────────────────────────────────────────
# INFORMATION SOURCES
# ─────────────────────────────────────────────

class TestInformationSources:
    @pytest.fixture(autouse=True)
    def setup(self, headers):
        self.h = headers

    def _create_source(self):
        ts = int(datetime.now().timestamp())
        return requests.post(f"{BASE_URL}/information-sources", headers=self.h, json={
            "name": f"Source_{ts}",
            "url": f"https://source{ts}.example.com/rss",
        })

    def test_list_sources(self):
        r = requests.get(f"{BASE_URL}/information-sources", headers=self.h)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_source_ok(self):
        r = self._create_source()
        assert r.status_code == 201
        body = r.json()
        assert "id" in body
        assert "url" in body

    def test_create_source_missing_name(self):
        r = requests.post(f"{BASE_URL}/information-sources", headers=self.h, json={
            "url": "https://example.com",
        })
        assert r.status_code == 422

    def test_create_source_invalid_url(self):
        r = requests.post(f"{BASE_URL}/information-sources", headers=self.h, json={
            "name": "Bad URL",
            "url": "no-es-una-url",
        })
        assert r.status_code == 422

    def test_get_source_ok(self):
        created = self._create_source().json()
        r = requests.get(f"{BASE_URL}/information-sources/{created['id']}", headers=self.h)
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_get_source_not_found(self):
        r = requests.get(f"{BASE_URL}/information-sources/999999", headers=self.h)
        assert r.status_code == 404

    def test_update_source_ok(self):
        created = self._create_source().json()
        r = requests.put(
            f"{BASE_URL}/information-sources/{created['id']}",
            headers=self.h,
            json={"name": "Updated Name"},
        )
        assert r.status_code == 200
        assert r.json()["name"] == "Updated Name"

    def test_update_source_not_found(self):
        r = requests.put(f"{BASE_URL}/information-sources/999999", headers=self.h, json={"name": "X"})
        assert r.status_code == 404

    def test_delete_source_ok(self):
        created = self._create_source().json()
        r = requests.delete(f"{BASE_URL}/information-sources/{created['id']}", headers=self.h)
        assert r.status_code == 204

        r2 = requests.get(f"{BASE_URL}/information-sources/{created['id']}", headers=self.h)
        assert r2.status_code == 404

    def test_delete_source_not_found(self):
        r = requests.delete(f"{BASE_URL}/information-sources/999999", headers=self.h)
        assert r.status_code == 404


# ─────────────────────────────────────────────
# RSS CHANNELS
# ─────────────────────────────────────────────

class TestRSSChannels:
    @pytest.fixture(autouse=True)
    def setup(self, headers):
        self.h = headers
        ts = datetime.now().timestamp()

        cat = requests.post(f"{BASE_URL}/categories", headers=self.h, json={
            "name": f"CatRSS_{ts}", "source": "IPTC",
        }).json()
        self.cat_id = cat["id"]

        src = requests.post(f"{BASE_URL}/information-sources", headers=self.h, json={
            "name": f"SrcRSS_{ts}", "url": f"https://srcrss{ts}.example.com/rss",
        }).json()
        self.src_id = src["id"]

    def _create_channel(self):
        ts = int(datetime.now().timestamp())
        return requests.post(
            f"{BASE_URL}/information-sources/{self.src_id}/rss-channels",
            headers=self.h,
            json={"url": f"https://feed{ts}.example.com/rss/feed.xml", "category_id": self.cat_id},
        )

    def test_list_channels(self):
        r = requests.get(
            f"{BASE_URL}/information-sources/{self.src_id}/rss-channels",
            headers=self.h,
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_channels_source_not_found(self):
        r = requests.get(f"{BASE_URL}/information-sources/999999/rss-channels", headers=self.h)
        assert r.status_code == 404

    def test_create_channel_ok(self):
        r = self._create_channel()
        assert r.status_code == 201
        body = r.json()
        assert "id" in body
        assert body["information_source_id"] == self.src_id
        assert body["category_id"] == self.cat_id

    def test_create_channel_source_not_found(self):
        r = requests.post(
            f"{BASE_URL}/information-sources/999999/rss-channels",
            headers=self.h,
            json={"url": "https://feed.example.com/rss", "category_id": self.cat_id},
        )
        assert r.status_code == 404

    def test_create_channel_category_not_found(self):
        r = requests.post(
            f"{BASE_URL}/information-sources/{self.src_id}/rss-channels",
            headers=self.h,
            json={"url": "https://feed.example.com/rss", "category_id": 999999},
        )
        assert r.status_code == 404

    def test_create_channel_invalid_url(self):
        r = requests.post(
            f"{BASE_URL}/information-sources/{self.src_id}/rss-channels",
            headers=self.h,
            json={"url": "no-es-url", "category_id": self.cat_id},
        )
        assert r.status_code == 422

    def test_get_channel_ok(self):
        created = self._create_channel().json()
        r = requests.get(
            f"{BASE_URL}/information-sources/{self.src_id}/rss-channels/{created['id']}",
            headers=self.h,
        )
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_get_channel_not_found(self):
        r = requests.get(
            f"{BASE_URL}/information-sources/{self.src_id}/rss-channels/999999",
            headers=self.h,
        )
        assert r.status_code == 404

    def test_get_channel_wrong_source(self):
        created = self._create_channel().json()
        # Crear otra fuente y buscar el canal en ella → 404
        ts = int(datetime.now().timestamp())
        other_src = requests.post(f"{BASE_URL}/information-sources", headers=self.h, json={
            "name": f"Other_{ts}", "url": f"https://other{ts}.example.com/rss",
        }).json()
        r = requests.get(
            f"{BASE_URL}/information-sources/{other_src['id']}/rss-channels/{created['id']}",
            headers=self.h,
        )
        assert r.status_code == 404

    def test_update_channel_ok(self):
        created = self._create_channel().json()
        ts = datetime.now().timestamp()
        r = requests.put(
            f"{BASE_URL}/information-sources/{self.src_id}/rss-channels/{created['id']}",
            headers=self.h,
            json={"url": f"https://updated{ts}.example.com/rss"},
        )
        assert r.status_code == 200

    def test_update_channel_invalid_category(self):
        created = self._create_channel().json()
        r = requests.put(
            f"{BASE_URL}/information-sources/{self.src_id}/rss-channels/{created['id']}",
            headers=self.h,
            json={"category_id": 999999},
        )
        assert r.status_code == 404

    def test_update_channel_not_found(self):
        r = requests.put(
            f"{BASE_URL}/information-sources/{self.src_id}/rss-channels/999999",
            headers=self.h,
            json={"url": "https://x.com/rss"},
        )
        assert r.status_code == 404

    def test_delete_channel_ok(self):
        created = self._create_channel().json()
        r = requests.delete(
            f"{BASE_URL}/information-sources/{self.src_id}/rss-channels/{created['id']}",
            headers=self.h,
        )
        assert r.status_code == 204

    def test_delete_channel_not_found(self):
        r = requests.delete(
            f"{BASE_URL}/information-sources/{self.src_id}/rss-channels/999999",
            headers=self.h,
        )
        assert r.status_code == 404


# ─────────────────────────────────────────────
# ALERTS
# ─────────────────────────────────────────────

class TestAlerts:
    @pytest.fixture(autouse=True)
    def setup(self, headers):
        self.h = headers
        roles = requests.get(f"{BASE_URL}/roles", headers=self.h).json()
        role_id = roles[0]["id"] if roles else None

        ts = datetime.now().timestamp()
        user = requests.post(f"{BASE_URL}/users", headers=self.h, json={
            "email": f"alert_user_{ts}@example.com",
            "first_name": "Alert",
            "last_name": "User",
            "organization": "UC3M",
            "password": "password123",
            "role_ids": [role_id] if role_id else [],
        }).json()
        self.user_id = user["id"]

    def _alert_payload(self):
        return {
            "name": f"Alerta_{datetime.now().timestamp()}",
            "descriptors": ["python", "ia"],
            "categories": [{"code": "04000000", "label": "Economía"}],
            "rss_channels_ids": [],
            "information_sources_ids": [],
            "cron_expression": "0 * * * *",
        }

    def test_list_alerts_ok(self):
        r = requests.get(f"{BASE_URL}/users/{self.user_id}/alerts", headers=self.h)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_alerts_user_not_found(self):
        r = requests.get(f"{BASE_URL}/users/999999/alerts", headers=self.h)
        assert r.status_code == 404

    def test_create_alert_ok(self):
        r = requests.post(
            f"{BASE_URL}/users/{self.user_id}/alerts",
            headers=self.h,
            json=self._alert_payload(),
        )
        assert r.status_code == 201
        body = r.json()
        assert "id" in body
        assert body["user_id"] == self.user_id

    def test_create_alert_user_not_found(self):
        r = requests.post(
            f"{BASE_URL}/users/999999/alerts",
            headers=self.h,
            json=self._alert_payload(),
        )
        assert r.status_code == 404

    def test_create_alert_missing_cron(self):
        payload = self._alert_payload()
        del payload["cron_expression"]
        r = requests.post(
            f"{BASE_URL}/users/{self.user_id}/alerts",
            headers=self.h,
            json=payload,
        )
        assert r.status_code == 422

    def test_create_alert_missing_name(self):
        payload = self._alert_payload()
        del payload["name"]
        r = requests.post(
            f"{BASE_URL}/users/{self.user_id}/alerts",
            headers=self.h,
            json=payload,
        )
        assert r.status_code == 422

    def test_get_alert_ok(self):
        created = requests.post(
            f"{BASE_URL}/users/{self.user_id}/alerts",
            headers=self.h,
            json=self._alert_payload(),
        ).json()

        r = requests.get(
            f"{BASE_URL}/users/{self.user_id}/alerts/{created['id']}",
            headers=self.h,
        )
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_get_alert_not_found(self):
        r = requests.get(
            f"{BASE_URL}/users/{self.user_id}/alerts/999999",
            headers=self.h,
        )
        assert r.status_code == 404

    def test_get_alert_wrong_user(self):
        created = requests.post(
            f"{BASE_URL}/users/{self.user_id}/alerts",
            headers=self.h,
            json=self._alert_payload(),
        ).json()

        roles = requests.get(f"{BASE_URL}/roles", headers=self.h).json()
        role_id = roles[0]["id"] if roles else None
        ts = datetime.now().timestamp()
        other_user = requests.post(f"{BASE_URL}/users", headers=self.h, json={
            "email": f"other_{ts}@example.com",
            "first_name": "Other",
            "last_name": "User",
            "organization": "UC3M",
            "password": "password123",
            "role_ids": [role_id] if role_id else [],
        }).json()

        r = requests.get(
            f"{BASE_URL}/users/{other_user['id']}/alerts/{created['id']}",
            headers=self.h,
        )
        assert r.status_code == 404

    def test_update_alert_ok(self):
        created = requests.post(
            f"{BASE_URL}/users/{self.user_id}/alerts",
            headers=self.h,
            json=self._alert_payload(),
        ).json()

        r = requests.put(
            f"{BASE_URL}/users/{self.user_id}/alerts/{created['id']}",
            headers=self.h,
            json={"name": "Alerta actualizada", "cron_expression": "*/30 * * * *"},
        )
        assert r.status_code == 200
        assert r.json()["name"] == "Alerta actualizada"

    def test_update_alert_not_found(self):
        r = requests.put(
            f"{BASE_URL}/users/{self.user_id}/alerts/999999",
            headers=self.h,
            json={"name": "X", "cron_expression": "* * * * *"},
        )
        assert r.status_code == 404

    def test_delete_alert_ok(self):
        created = requests.post(
            f"{BASE_URL}/users/{self.user_id}/alerts",
            headers=self.h,
            json=self._alert_payload(),
        ).json()

        r = requests.delete(
            f"{BASE_URL}/users/{self.user_id}/alerts/{created['id']}",
            headers=self.h,
        )
        assert r.status_code == 204

    def test_delete_alert_not_found(self):
        r = requests.delete(
            f"{BASE_URL}/users/{self.user_id}/alerts/999999",
            headers=self.h,
        )
        assert r.status_code == 404


# ─────────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────────

class TestNotifications:
    @pytest.fixture(autouse=True)
    def setup(self, headers):
        self.h = headers
        roles = requests.get(f"{BASE_URL}/roles", headers=self.h).json()
        role_id = roles[0]["id"] if roles else None

        ts = datetime.now().timestamp()
        user = requests.post(f"{BASE_URL}/users", headers=self.h, json={
            "email": f"notif_user_{ts}@example.com",
            "first_name": "Notif",
            "last_name": "User",
            "organization": "UC3M",
            "password": "password123",
            "role_ids": [role_id] if role_id else [],
        }).json()
        self.user_id = user["id"]

        alert = requests.post(f"{BASE_URL}/users/{self.user_id}/alerts", headers=self.h, json={
            "name": f"AlertNotif_{ts}",
            "descriptors": ["test"],
            "categories": [],
            "rss_channels_ids": [],
            "information_sources_ids": [],
            "cron_expression": "0 * * * *",
        }).json()
        self.alert_id = alert["id"]

    def _notif_payload(self):
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": [{"name": "noticias_procesadas", "value": 5}],
            "title": "Actualización de alerta",
            "content": "Se encontraron 5 noticias.",
        }

    def test_list_notifications_ok(self):
        r = requests.get(
            f"{BASE_URL}/users/{self.user_id}/alerts/{self.alert_id}/notifications",
            headers=self.h,
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_notifications_alert_not_found(self):
        r = requests.get(
            f"{BASE_URL}/users/{self.user_id}/alerts/999999/notifications",
            headers=self.h,
        )
        assert r.status_code == 404

    def test_create_notification_ok(self):
        r = requests.post(
            f"{BASE_URL}/users/{self.user_id}/alerts/{self.alert_id}/notifications",
            headers=self.h,
            json=self._notif_payload(),
        )
        assert r.status_code == 201
        body = r.json()
        assert "id" in body
        assert body["alert_id"] == self.alert_id

    def test_create_notification_with_news(self):
        payload = self._notif_payload()
        payload["news"] = [{
            "title": "Noticia de prueba",
            "link": "https://example.com/noticia",
            "source_name": "El País",
            "category": "Tecnología",
            "published": datetime.now(timezone.utc).isoformat(),
        }]
        r = requests.post(
            f"{BASE_URL}/users/{self.user_id}/alerts/{self.alert_id}/notifications",
            headers=self.h,
            json=payload,
        )
        assert r.status_code == 201

    def test_create_notification_alert_not_found(self):
        r = requests.post(
            f"{BASE_URL}/users/{self.user_id}/alerts/999999/notifications",
            headers=self.h,
            json=self._notif_payload(),
        )
        assert r.status_code == 404

    def test_create_notification_missing_timestamp(self):
        payload = self._notif_payload()
        del payload["timestamp"]
        r = requests.post(
            f"{BASE_URL}/users/{self.user_id}/alerts/{self.alert_id}/notifications",
            headers=self.h,
            json=payload,
        )
        assert r.status_code == 422

    def test_get_notification_ok(self):
        created = requests.post(
            f"{BASE_URL}/users/{self.user_id}/alerts/{self.alert_id}/notifications",
            headers=self.h,
            json=self._notif_payload(),
        ).json()

        r = requests.get(
            f"{BASE_URL}/users/{self.user_id}/alerts/{self.alert_id}/notifications/{created['id']}",
            headers=self.h,
        )
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_get_notification_not_found(self):
        r = requests.get(
            f"{BASE_URL}/users/{self.user_id}/alerts/{self.alert_id}/notifications/999999",
            headers=self.h,
        )
        assert r.status_code == 404

    def test_update_notification_ok(self):
        created = requests.post(
            f"{BASE_URL}/users/{self.user_id}/alerts/{self.alert_id}/notifications",
            headers=self.h,
            json=self._notif_payload(),
        ).json()

        r = requests.put(
            f"{BASE_URL}/users/{self.user_id}/alerts/{self.alert_id}/notifications/{created['id']}",
            headers=self.h,
            json={"title": "Título actualizado", "content": "Nuevo contenido"},
        )
        assert r.status_code == 200
        assert r.json()["title"] == "Título actualizado"

    def test_update_notification_not_found(self):
        r = requests.put(
            f"{BASE_URL}/users/{self.user_id}/alerts/{self.alert_id}/notifications/999999",
            headers=self.h,
            json={"title": "X"},
        )
        assert r.status_code == 404

    def test_delete_notification_ok(self):
        created = requests.post(
            f"{BASE_URL}/users/{self.user_id}/alerts/{self.alert_id}/notifications",
            headers=self.h,
            json=self._notif_payload(),
        ).json()

        r = requests.delete(
            f"{BASE_URL}/users/{self.user_id}/alerts/{self.alert_id}/notifications/{created['id']}",
            headers=self.h,
        )
        assert r.status_code == 204

    def test_delete_notification_not_found(self):
        r = requests.delete(
            f"{BASE_URL}/users/{self.user_id}/alerts/{self.alert_id}/notifications/999999",
            headers=self.h,
        )
        assert r.status_code == 404


# ─────────────────────────────────────────────
# STATS
# ─────────────────────────────────────────────

class TestStats:
    @pytest.fixture(autouse=True)
    def setup(self, headers):
        self.h = headers

    def _stats_payload(self):
        return {
            "metrics": [
                {"name": "fuentes", "value": 45},
                {"name": "noticias", "value": 3200},
            ]
        }

    def test_list_stats(self):
        r = requests.get(f"{BASE_URL}/stats", headers=self.h)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_stats_ok(self):
        r = requests.post(f"{BASE_URL}/stats", headers=self.h, json=self._stats_payload())
        assert r.status_code == 201
        body = r.json()
        assert "id" in body
        assert len(body["metrics"]) == 2

    def test_create_stats_empty_metrics(self):
        r = requests.post(f"{BASE_URL}/stats", headers=self.h, json={"metrics": []})
        assert r.status_code == 201

    def test_create_stats_missing_metric_fields(self):
        r = requests.post(f"{BASE_URL}/stats", headers=self.h, json={
            "metrics": [{"name": "fuentes"}]  # falta value
        })
        assert r.status_code == 422

    def test_get_stats_ok(self):
        created = requests.post(f"{BASE_URL}/stats", headers=self.h, json=self._stats_payload()).json()
        r = requests.get(f"{BASE_URL}/stats/{created['id']}", headers=self.h)
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_get_stats_not_found(self):
        r = requests.get(f"{BASE_URL}/stats/999999", headers=self.h)
        assert r.status_code == 404

    def test_update_stats_ok(self):
        created = requests.post(f"{BASE_URL}/stats", headers=self.h, json=self._stats_payload()).json()
        r = requests.put(f"{BASE_URL}/stats/{created['id']}", headers=self.h, json={
            "metrics": [{"name": "alertas", "value": 10}]
        })
        assert r.status_code == 200
        assert r.json()["metrics"][0]["name"] == "alertas"

    def test_update_stats_not_found(self):
        r = requests.put(f"{BASE_URL}/stats/999999", headers=self.h, json={"metrics": []})
        assert r.status_code == 404

    def test_delete_stats_ok(self):
        created = requests.post(f"{BASE_URL}/stats", headers=self.h, json=self._stats_payload()).json()
        r = requests.delete(f"{BASE_URL}/stats/{created['id']}", headers=self.h)
        assert r.status_code == 204

        r2 = requests.get(f"{BASE_URL}/stats/{created['id']}", headers=self.h)
        assert r2.status_code == 404

    def test_delete_stats_not_found(self):
        r = requests.delete(f"{BASE_URL}/stats/999999", headers=self.h)
        assert r.status_code == 404


# ─────────────────────────────────────────────
# DASHBOARD & WORDCLOUD
# ─────────────────────────────────────────────

class TestDashboard:
    @pytest.fixture(autouse=True)
    def setup(self, headers):
        self.h = headers

    def test_get_dashboard_ok(self):
        r = requests.get(f"{BASE_URL}/dashboard", headers=self.h)
        assert r.status_code == 200
        body = r.json()
        assert "fuentes" in body
        assert "noticias" in body
        assert "alertas" in body
        assert "evolucion" in body
        assert "categorias" in body

    def test_get_dashboard_with_days_param(self):
        r = requests.get(f"{BASE_URL}/dashboard?days=30", headers=self.h)
        assert r.status_code == 200

    def test_get_dashboard_no_auth(self):
        r = requests.get(f"{BASE_URL}/dashboard")
        assert r.status_code in (401, 403)

    def test_get_wordcloud_global(self):
        r = requests.get(f"{BASE_URL}/resumen/clouds/global", headers=self.h)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_wordcloud_global_with_params(self):
        r = requests.get(f"{BASE_URL}/resumen/clouds/global?days=7&limit=10", headers=self.h)
        assert r.status_code == 200

    def test_get_wordcloud_by_category(self):
        r = requests.get(f"{BASE_URL}/resumen/clouds/technology", headers=self.h)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_wordcloud_by_category_no_auth(self):
        r = requests.get(f"{BASE_URL}/resumen/clouds/technology")
        assert r.status_code in (401, 403)