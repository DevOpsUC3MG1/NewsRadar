"""Targeted tests to increase coverage — analytics, auth, and edge cases."""

from uuid import uuid4
from datetime import datetime, timezone, timedelta


# =========================================================================
#  ANALYTICS — dashboard & wordcloud with mock MongoDB data
# =========================================================================


async def test_dashboard_with_notifications(client, gestor_headers):
    """Cover _notification_news_stats path with actual notifications."""
    now = datetime.now(timezone.utc).isoformat()
    suffix = uuid4().hex[:8]

    resp = await client.post("/api/v1/users/1/alerts", json={
        "name": f"DashAlert-{suffix}", "cron_expression": "0 0 * * *",
        "descriptors": [f"tag-{suffix}"],
    }, headers=gestor_headers)
    alert_id = resp.json()["id"]

    await client.post(f"/api/v1/users/1/alerts/{alert_id}/notifications", json={
        "timestamp": now, "title": "DashNotif",
        "metrics": [{"name": "articles_detected", "value": 3}],
    }, headers=gestor_headers)

    response = await client.get("/api/v1/dashboard?days=7", headers=gestor_headers)
    assert response.status_code == 200
    data = response.json()
    assert "fuentes" in data
    assert "noticias" in data
    assert "alertas" in data


async def test_wordcloud_global_with_data(client, gestor_headers):
    """Cover build_wordcloud with articles in notifications."""
    now = datetime.now(timezone.utc).isoformat()
    suffix = uuid4().hex[:8]

    resp = await client.post("/api/v1/users/1/alerts", json={
        "name": f"WCAlert-{suffix}", "cron_expression": "0 0 * * *",
        "descriptors": [f"tag-{suffix}"],
    }, headers=gestor_headers)
    alert_id = resp.json()["id"]

    articles = [{
        "title": f"Article {i}",
        "link": f"https://example.com/{i}",
        "source_name": "Test",
        "category": "Economía",
        "published": now,
        "description": "economic crisis inflation" * 5,
    } for i in range(3)]

    await client.post(f"/api/v1/users/1/alerts/{alert_id}/notifications", json={
        "timestamp": now, "title": "WCNotif",
        "news": articles,
    }, headers=gestor_headers)

    response = await client.get("/api/v1/resumen/clouds/global?days=30&limit=5", headers=gestor_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_wordcloud_by_iptc_category(client, gestor_headers):
    """Cover build_wordcloud with IPTC numeric category filter."""
    now = datetime.now(timezone.utc).isoformat()
    suffix = uuid4().hex[:8]

    resp = await client.post("/api/v1/users/1/alerts", json={
        "name": f"WCCatAlert-{suffix}", "cron_expression": "0 0 * * *",
        "descriptors": [f"tag-{suffix}"],
    }, headers=gestor_headers)
    alert_id = resp.json()["id"]

    articles = [{
        "title": f"Economy Article {i}",
        "link": f"https://example.com/econ/{i}",
        "source_name": "Test",
        "category": "Economía",
        "published": now,
        "description": "market prices economy finance" * 5,
    } for i in range(2)]

    await client.post(f"/api/v1/users/1/alerts/{alert_id}/notifications", json={
        "timestamp": now, "title": "WCCatNotif",
        "news": articles,
    }, headers=gestor_headers)

    response = await client.get("/api/v1/resumen/clouds/4000000?days=30&limit=5", headers=gestor_headers)
    assert response.status_code == 200


# =========================================================================
#  AUTH — verify / resend / forgot-password / reset-password edge cases
# =========================================================================


async def test_verify_account_invalid_token(client):
    response = await client.post("/api/v1/auth/verify", json={"token": "bad-token"})
    assert response.status_code == 404


async def test_verify_account_expired_token(client, gestor_headers):
    """Register, then try to verify with a non-existent/expired token."""
    suffix = uuid4().hex[:8]
    email = f"expired-{suffix}@test.es"
    await client.post("/api/v1/auth/register", json={
        "email": email, "password": "Pass123!",
        "first_name": "Exp", "last_name": "Test",
    })
    response = await client.post("/api/v1/auth/verify", json={"token": "expired-or-nonexistent"})
    assert response.status_code == 404


async def test_resend_verification_known_email(client):
    suffix = uuid4().hex[:8]
    email = f"resend-{suffix}@test.es"
    await client.post("/api/v1/auth/register", json={
        "email": email, "password": "Pass123!",
    })
    response = await client.post("/api/v1/auth/resend-verification", json={"email": email})
    assert response.status_code == 200


async def test_resend_verification_unknown_email(client):
    response = await client.post("/api/v1/auth/resend-verification",
                                 json={"email": "ghost@test.es"})
    assert response.status_code == 404


async def test_forgot_password(client):
    response = await client.post("/api/v1/auth/forgot-password",
                                 json={"email": "admin@newsradar.com"})
    assert response.status_code == 200


async def test_reset_password_invalid(client):
    response = await client.post("/api/v1/auth/reset-password", json={
        "token": "bad-reset-token",
        "new_password": "NewPass123!",
    })
    assert response.status_code == 400


# =========================================================================
#  USERS — edge cases
# =========================================================================


async def test_create_user_duplicate_email(client, gestor_headers):
    response = await client.post("/api/v1/users", json={
        "email": "admin@newsradar.com", "password": "Pass123!",
        "first_name": "Dup", "last_name": "User",
    }, headers=gestor_headers)
    assert response.status_code == 409


async def test_create_user_two_roles_rejected(client, gestor_headers):
    """The API allows max 1 role per user."""
    suffix = uuid4().hex[:8]
    response = await client.post("/api/v1/users", json={
        "email": f"multirole-{suffix}@test.es", "password": "Pass123!",
        "first_name": "Multi", "last_name": "Role",
        "role_ids": [1, 2],
    }, headers=gestor_headers)
    assert response.status_code == 422


async def test_get_user_not_found(client, gestor_headers):
    response = await client.get("/api/v1/users/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_update_user_not_found(client, gestor_headers):
    response = await client.put("/api/v1/users/99999", json={"first_name": "Ghost"},
                                headers=gestor_headers)
    assert response.status_code == 404


async def test_get_verification_status(client, gestor_headers):
    response = await client.get("/api/v1/users/email/admin@newsradar.com/verification-status",
                                headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "admin@newsradar.com"
    assert "is_verified" in response.json()


async def test_get_verification_status_not_found(client, gestor_headers):
    response = await client.get("/api/v1/users/email/nonexistent@test.es/verification-status",
                                headers=gestor_headers)
    assert response.status_code == 404


# =========================================================================
#  ROLES — duplicate name, edge response cases
# =========================================================================


async def test_create_role_duplicate_name(client, gestor_headers):
    suffix = uuid4().hex[:8]
    name = f"role-dup-{suffix}"
    resp1 = await client.post("/api/v1/roles", json={"name": name}, headers=gestor_headers)
    assert resp1.status_code == 201
    resp2 = await client.post("/api/v1/roles", json={"name": name}, headers=gestor_headers)
    assert resp2.status_code == 409


async def test_get_role_not_found(client, gestor_headers):
    response = await client.get("/api/v1/roles/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_update_role_not_found(client, gestor_headers):
    response = await client.put("/api/v1/roles/99999", json={"name": "Ghost"},
                                headers=gestor_headers)
    assert response.status_code == 404


async def test_delete_role_with_users(client, gestor_headers):
    """Can't delete a role assigned to users."""
    response = await client.delete("/api/v1/roles/1", headers=gestor_headers)
    assert response.status_code == 409


async def test_delete_role_not_found(client, gestor_headers):
    response = await client.delete("/api/v1/roles/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_create_role_name_too_long(client, gestor_headers):
    response = await client.post("/api/v1/roles", json={"name": "x" * 101},
                                 headers=gestor_headers)
    assert response.status_code == 422


async def test_create_role_control_chars(client, gestor_headers):
    response = await client.post("/api/v1/roles", json={"name": "test\nrole"},
                                 headers=gestor_headers)
    assert response.status_code == 422


async def test_create_role_empty_name(client, gestor_headers):
    response = await client.post("/api/v1/roles", json={"name": ""},
                                 headers=gestor_headers)
    assert response.status_code == 422


# =========================================================================
#  ALERTS — validation edge cases
# =========================================================================


async def test_create_alert_invalid_cron(client, gestor_headers, clean_alerts):
    response = await client.post("/api/v1/users/1/alerts", json={
        "name": "BadCron", "cron_expression": "not-a-cron",
    }, headers=gestor_headers)
    assert response.status_code == 422


async def test_create_alert_missing_name(client, gestor_headers, clean_alerts):
    response = await client.post("/api/v1/users/1/alerts", json={
        "cron_expression": "0 0 * * *",
    }, headers=gestor_headers)
    assert response.status_code == 422


async def test_create_alert_duplicate_descriptors(client, gestor_headers, clean_alerts):
    suffix = uuid4().hex[:8]
    response = await client.post("/api/v1/users/1/alerts", json={
        "name": f"DupDesc-{suffix}", "cron_expression": "0 0 * * *",
        "descriptors": ["dup", "dup"],
    }, headers=gestor_headers)
    assert response.status_code == 422


async def test_get_alert_not_found(client, gestor_headers):
    response = await client.get("/api/v1/users/1/alerts/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_update_alert_not_found(client, gestor_headers):
    response = await client.put("/api/v1/users/1/alerts/99999", json={"name": "Ghost"},
                                headers=gestor_headers)
    assert response.status_code == 404


async def test_delete_alert_not_found(client, gestor_headers):
    response = await client.delete("/api/v1/users/1/alerts/99999", headers=gestor_headers)
    assert response.status_code == 404


# =========================================================================
#  CATEGORIES — edge cases
# =========================================================================


async def test_create_category_invalid_name(client, gestor_headers):
    response = await client.post("/api/v1/categories", json={
        "name": "NotInIPTC", "source": "IPTC",
    }, headers=gestor_headers)
    assert response.status_code == 422


async def test_get_category_not_found(client, gestor_headers):
    response = await client.get("/api/v1/categories/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_update_category_not_found(client, gestor_headers):
    response = await client.put("/api/v1/categories/99999", json={
        "name": "Economía, negocios y finanzas",
    }, headers=gestor_headers)
    assert response.status_code == 404


# =========================================================================
#  INFORMATION SOURCES — edge cases
# =========================================================================


async def test_get_information_source_not_found(client, gestor_headers):
    response = await client.get("/api/v1/information-sources/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_update_information_source_not_found(client, gestor_headers):
    response = await client.put("/api/v1/information-sources/99999", json={"name": "Ghost"},
                                headers=gestor_headers)
    assert response.status_code == 404


async def test_delete_information_source_not_found(client, gestor_headers):
    response = await client.delete("/api/v1/information-sources/99999", headers=gestor_headers)
    assert response.status_code == 404


# =========================================================================
#  STATS — edge cases
# =========================================================================


async def test_get_stats_not_found(client, gestor_headers):
    response = await client.get("/api/v1/stats/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_update_stats_not_found(client, gestor_headers):
    response = await client.put("/api/v1/stats/99999", json={"metrics": []},
                                headers=gestor_headers)
    assert response.status_code == 404


async def test_delete_stats_not_found(client, gestor_headers):
    response = await client.delete("/api/v1/stats/99999", headers=gestor_headers)
    assert response.status_code == 404
