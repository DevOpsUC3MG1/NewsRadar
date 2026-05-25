"""Edge-case and error-path tests to increase coverage"""

from uuid import uuid4
import pytest

pytestmark = pytest.mark.usefixtures("clean_alerts")


async def test_create_alert_duplicate_name(client, gestor_headers):
    suffix = uuid4().hex[:8]
    payload = {"name": f"Duplicada-{suffix}", "cron_expression": "0 0 * * *", "descriptors": [f"tag-{suffix}"]}
    resp1 = await client.post("/api/v1/users/1/alerts", json=payload, headers=gestor_headers)
    assert resp1.status_code == 201
    resp2 = await client.post("/api/v1/users/1/alerts", json=payload, headers=gestor_headers)
    assert resp2.status_code == 409


async def test_create_alert_duplicate_descriptors(client, gestor_headers):
    suffix = uuid4().hex[:8]
    payload = {"name": f"DescDupe-{suffix}", "cron_expression": "0 0 * * *", "descriptors": ["dup", "dup"]}
    response = await client.post("/api/v1/users/1/alerts", json=payload, headers=gestor_headers)
    assert response.status_code == 422


async def test_create_role_duplicate(client, gestor_headers):
    suffix = uuid4().hex[:8]
    name = f"test_dupe_role_{suffix}"
    resp1 = await client.post("/api/v1/roles", json={"name": name}, headers=gestor_headers)
    assert resp1.status_code == 201
    resp2 = await client.post("/api/v1/roles", json={"name": name}, headers=gestor_headers)
    assert resp2.status_code == 409


async def test_create_alert_missing_fields(client, gestor_headers):
    payload = {"name": "Incomplete"}
    response = await client.post("/api/v1/users/1/alerts", json=payload, headers=gestor_headers)
    assert response.status_code == 422


async def test_get_user_by_email_verification_status(client, gestor_headers):
    response = await client.get("/api/v1/users/email/admin@newsradar.com/verification-status", headers=gestor_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@newsradar.com"
    assert "is_verified" in data


async def test_get_user_verification_status_not_found(client, gestor_headers):
    response = await client.get("/api/v1/users/email/nonexistent@test.com/verification-status", headers=gestor_headers)
    assert response.status_code == 404


async def test_unauthorized_access(client):
    response = await client.get("/api/v1/users")
    assert response.status_code == 401


async def test_unauthorized_access_alert_create(client):
    payload = {"name": "Blocked", "cron_expression": "0 0 * * *", "descriptors": ["test"]}
    response = await client.post("/api/v1/users/1/alerts", json=payload)
    assert response.status_code == 401


async def test_create_user_xss_sanitization(client, gestor_headers):
    suffix = uuid4().hex[:8]
    payload = {
        "email": f"xss-{suffix}@newsradar.es", "password": "XssPass123!",
        "first_name": "<script>alert('xss')</script>", "last_name": "User<script>",
        "organization": "NewsRadar",
    }
    response = await client.post("/api/v1/users", json=payload, headers=gestor_headers)
    assert response.status_code == 201
    data = response.json()
    assert "<" not in data["first_name"]
    assert "<" not in data["last_name"]


async def test_create_user_multiple_roles_rejected(client, gestor_headers):
    suffix = uuid4().hex[:8]
    payload = {
        "email": f"multirole-{suffix}@newsradar.es", "password": "Multi123!",
        "first_name": "Multi", "last_name": "Role", "organization": "NewsRadar",
        "role_ids": [1, 2],
    }
    response = await client.post("/api/v1/users", json=payload, headers=gestor_headers)
    assert response.status_code == 422


async def test_create_role_name_too_long(client, gestor_headers):
    response = await client.post("/api/v1/roles", json={"name": "a" * 101}, headers=gestor_headers)
    assert response.status_code == 422


async def test_create_role_name_with_control_chars(client, gestor_headers):
    response = await client.post("/api/v1/roles", json={"name": "test\nrole"}, headers=gestor_headers)
    assert response.status_code == 422


async def test_create_alert_empty_descriptor_skipped(client, gestor_headers):
    suffix = uuid4().hex[:8]
    payload = {"name": f"EmptyDesc-{suffix}", "cron_expression": "0 0 * * *", "descriptors": ["", "valid"]}
    response = await client.post("/api/v1/users/1/alerts", json=payload, headers=gestor_headers)
    assert response.status_code == 201


async def test_create_information_source_duplicate_name(client, gestor_headers):
    from uuid import uuid4
    suffix = uuid4().hex[:8]
    url = f"https://dup-name-{suffix}.com"
    payload = {"name": f"Duplicate Name Test {suffix}", "url": url}
    resp1 = await client.post("/api/v1/information-sources", json=payload, headers=gestor_headers)
    assert resp1.status_code == 201
    resp2 = await client.post("/api/v1/information-sources", json=payload, headers=gestor_headers)
    assert resp2.status_code == 409


async def test_create_information_source_duplicate_url(client, gestor_headers):
    from uuid import uuid4
    suffix = uuid4().hex[:8]
    url = f"https://dup-url-{suffix}.com"
    payload = {"name": f"First {suffix}", "url": url}
    resp1 = await client.post("/api/v1/information-sources", json=payload, headers=gestor_headers)
    assert resp1.status_code == 201
    payload2 = {"name": f"Second {suffix}", "url": url}
    resp2 = await client.post("/api/v1/information-sources", json=payload2, headers=gestor_headers)
    assert resp2.status_code == 409


async def test_create_rss_channel_duplicate_url(client, gestor_headers):
    from uuid import uuid4
    suffix = uuid4().hex[:8]
    cat_resp = await client.post("/api/v1/categories", json={"name": "Medio ambiente", "source": "IPTC"}, headers=gestor_headers)
    if cat_resp.status_code == 409:
        list_resp = await client.get("/api/v1/categories", headers=gestor_headers)
        cat_id = next(c["id"] for c in list_resp.json() if c["name"] == "Medio ambiente")
    else:
        cat_id = cat_resp.json()["id"]
    src_resp = await client.post("/api/v1/information-sources", json={"name": f"RSS Dup Source {suffix}", "url": f"https://rss-dup-{suffix}.com"}, headers=gestor_headers)
    src_id = src_resp.json()["id"]
    ch_payload = {"url": f"https://rss-dup-{suffix}.com/feed", "category_id": cat_id}
    resp1 = await client.post(f"/api/v1/information-sources/{src_id}/rss-channels", json=ch_payload, headers=gestor_headers)
    assert resp1.status_code == 201
    resp2 = await client.post(f"/api/v1/information-sources/{src_id}/rss-channels", json=ch_payload, headers=gestor_headers)
    assert resp2.status_code == 409


async def test_create_information_source_unreachable_url(client, gestor_headers):
    payload = {"name": "Unreachable", "url": "http://inexistente.test/rss"}
    response = await client.post("/api/v1/information-sources", json=payload, headers=gestor_headers)
    assert response.status_code == 422
