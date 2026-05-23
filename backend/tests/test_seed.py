"""Tests for seed.py — pure functions (no DB)"""


def test_find_data_root():
    from newsradar_api.app.seed import _find_data_root
    root = _find_data_root()
    assert root is not None
    assert (root / "data").exists()


def test_load_rss_sources():
    from newsradar_api.app.seed import load_rss_sources
    data = load_rss_sources()
    assert isinstance(data, dict)
    assert "categories" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0


def test_load_iptc_catalog():
    from newsradar_api.app.seed import load_iptc_catalog
    catalog = load_iptc_catalog()
    assert isinstance(catalog, list)
    assert len(catalog) > 0
    assert "name" in catalog[0]
