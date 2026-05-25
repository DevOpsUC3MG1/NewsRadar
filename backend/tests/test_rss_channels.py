from uuid import uuid4


async def _ensure_category(client, gestor_headers, name):
    """Create category if it doesn't exist, return its id."""
    resp = await client.post("/api/v1/categories", json={"name": name, "source": "IPTC"}, headers=gestor_headers)
    if resp.status_code == 409:
        # Already exists — find it
        list_resp = await client.get("/api/v1/categories", headers=gestor_headers)
        for cat in list_resp.json():
            if cat["name"] == name:
                return cat["id"]
    assert resp.status_code == 201, f"Category creation failed: {resp.text}"
    return resp.json()["id"]


async def _ensure_source(client, gestor_headers, name, url):
    """Create source if it doesn't exist, return its id."""
    resp = await client.post("/api/v1/information-sources", json={"name": name, "url": url}, headers=gestor_headers)
    if resp.status_code == 409:
        list_resp = await client.get("/api/v1/information-sources", headers=gestor_headers)
        for src in list_resp.json():
            if src["name"] == name:
                return src["id"]
    assert resp.status_code == 201, f"Source creation failed: {resp.text}"
    return resp.json()["id"]


async def _create_source_and_category(client, gestor_headers):
    suffix = uuid4().hex[:8]
    # Try to create a known IPTC category; if it already exists, grab it from the list
    cat_resp = await client.post("/api/v1/categories", json={"name": "Medio ambiente", "source": "IPTC"}, headers=gestor_headers)
    if cat_resp.status_code == 409:
        list_resp = await client.get("/api/v1/categories", headers=gestor_headers)
        cat_id = next(c["id"] for c in list_resp.json() if c["name"] == "Medio ambiente")
    else:
        assert cat_resp.status_code == 201, f"Category creation failed: {cat_resp.text}"
        cat_id = cat_resp.json()["id"]

    src_url = f"https://rss-test-{suffix}.com"
    src_resp = await client.post("/api/v1/information-sources", json={"name": f"RSS Source {suffix}", "url": src_url}, headers=gestor_headers)
    assert src_resp.status_code == 201, f"Source creation failed: {src_resp.text}"
    src_id = src_resp.json()["id"]
    return src_id, cat_id


async def test_list_rss_channels(client, gestor_headers):
    src_id, cat_id = await _create_source_and_category(client, gestor_headers)
    response = await client.get(f"/api/v1/information-sources/{src_id}/rss-channels", headers=gestor_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_create_rss_channel(client, gestor_headers):
    suffix = uuid4().hex[:8]
    src_id, cat_id = await _create_source_and_category(client, gestor_headers)
    url = f"https://rss-create-{suffix}.com/feed"
    payload = {"url": url, "category_id": cat_id}
    response = await client.post(f"/api/v1/information-sources/{src_id}/rss-channels", json=payload, headers=gestor_headers)
    assert response.status_code == 201
    assert response.json()["url"] == url


async def test_get_rss_channel(client, gestor_headers):
    suffix = uuid4().hex[:8]
    src_id, cat_id = await _create_source_and_category(client, gestor_headers)
    url = f"https://rss-get-{suffix}.com/rss"
    create_resp = await client.post(f"/api/v1/information-sources/{src_id}/rss-channels", json={"url": url, "category_id": cat_id}, headers=gestor_headers)
    ch_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/information-sources/{src_id}/rss-channels/{ch_id}", headers=gestor_headers)
    assert response.status_code == 200
    assert response.json()["url"] == url


async def test_get_rss_channel_not_found(client, gestor_headers):
    src_id, cat_id = await _create_source_and_category(client, gestor_headers)
    response = await client.get(f"/api/v1/information-sources/{src_id}/rss-channels/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_update_rss_channel(client, gestor_headers):
    suffix = uuid4().hex[:8]
    src_id, cat_id = await _create_source_and_category(client, gestor_headers)
    create_resp = await client.post(f"/api/v1/information-sources/{src_id}/rss-channels", json={"url": f"https://rss-old-{suffix}.com", "category_id": cat_id}, headers=gestor_headers)
    ch_id = create_resp.json()["id"]

    new_url = f"https://rss-new-{suffix}.com"
    response = await client.put(f"/api/v1/information-sources/{src_id}/rss-channels/{ch_id}", json={"url": new_url}, headers=gestor_headers)
    assert response.status_code == 200
    # Pydantic HttpUrl normalizes with trailing slash
    assert response.json()["url"].rstrip("/") == new_url


async def test_update_rss_channel_not_found(client, gestor_headers):
    src_id, cat_id = await _create_source_and_category(client, gestor_headers)
    response = await client.put(f"/api/v1/information-sources/{src_id}/rss-channels/99999", json={"url": "https://nope.com"}, headers=gestor_headers)
    assert response.status_code == 404


async def test_delete_rss_channel(client, gestor_headers):
    suffix = uuid4().hex[:8]
    src_id, cat_id = await _create_source_and_category(client, gestor_headers)
    url = f"https://rss-del-{suffix}.com"
    create_resp = await client.post(f"/api/v1/information-sources/{src_id}/rss-channels", json={"url": url, "category_id": cat_id}, headers=gestor_headers)
    ch_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/information-sources/{src_id}/rss-channels/{ch_id}", headers=gestor_headers)
    assert response.status_code == 204

    get_resp = await client.get(f"/api/v1/information-sources/{src_id}/rss-channels/{ch_id}", headers=gestor_headers)
    assert get_resp.status_code == 404


async def test_delete_rss_channel_not_found(client, gestor_headers):
    src_id, cat_id = await _create_source_and_category(client, gestor_headers)
    response = await client.delete(f"/api/v1/information-sources/{src_id}/rss-channels/99999", headers=gestor_headers)
    assert response.status_code == 404


async def test_create_rss_channel_invalid_url(client, gestor_headers):
    src_id, cat_id = await _create_source_and_category(client, gestor_headers)
    payload = {"url": "not-a-url", "category_id": cat_id}
    response = await client.post(f"/api/v1/information-sources/{src_id}/rss-channels", json=payload, headers=gestor_headers)
    assert response.status_code == 422


async def test_rss_limit_per_source(client, gestor_headers):
    """T4_RSS_LIMIT_MEDIA: Ensure no more than 5 RSS channels can be created per source."""
    # Ensure category
    cat_id = await _ensure_category(client, gestor_headers, "General")

    # Ensure source FOXNews
    source_name = "FOXNews"
    source_url = "https://www.foxnews.com/"
    src_id = await _ensure_source(client, gestor_headers, source_name, source_url)

    # Five valid channels
    urls = [
        "https://moxie.foxnews.com/google-publisher/latest.xml",
        "https://moxie.foxnews.com/google-publisher/world.xml",
        "https://moxie.foxnews.com/google-publisher/politics.xml",
        "https://moxie.foxnews.com/google-publisher/science.xml",
        "https://moxie.foxnews.com/google-publisher/health.xml",
    ]

    for u in urls:
        resp = await client.post(f"/api/v1/information-sources/{src_id}/rss-channels", json={"url": u, "category_id": cat_id}, headers=gestor_headers)
        assert resp.status_code == 201, f"Failed creating allowed channel {u}: {resp.text}"

    # Sixth channel should fail with 400 or 403
    sixth = "https://moxie.foxnews.com/google-publisher/sports.xml"
    resp6 = await client.post(f"/api/v1/information-sources/{src_id}/rss-channels", json={"url": sixth, "category_id": cat_id}, headers=gestor_headers)
    assert resp6.status_code in (400, 403), f"Expected 400/403 for sixth channel, got {resp6.status_code}: {resp6.text}"

    # Verify there are exactly 5 channels for the source
    list_resp = await client.get(f"/api/v1/information-sources/{src_id}/rss-channels", headers=gestor_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 5, f"Expected 5 channels, found {len(list_resp.json())}"
