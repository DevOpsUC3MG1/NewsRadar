"""Unit tests for keyword_service — pure functions, no DB needed"""


def test_classify_iptc_level1_general():
    from newsradar_api.app.services.keyword_service import classify_iptc_level1
    assert classify_iptc_level1("") == "General"
    assert classify_iptc_level1("short") == "General"
    assert classify_iptc_level1("   ") == "General"


def test_classify_iptc_level1_politics():
    from newsradar_api.app.services.keyword_service import classify_iptc_level1
    result = classify_iptc_level1("El presidente aprobó el presupuesto en el congreso")
    assert result == "Politics"


def test_classify_iptc_level1_business():
    from newsradar_api.app.services.keyword_service import classify_iptc_level1
    result = classify_iptc_level1("La bolsa y los mercados financieros caen por la inflación")
    assert result == "Business"


def test_classify_iptc_level1_sports():
    from newsradar_api.app.services.keyword_service import classify_iptc_level1
    result = classify_iptc_level1("El futbol y la liga de campeones")
    assert result == "Sports"


def test_classify_iptc_level1_technology():
    from newsradar_api.app.services.keyword_service import classify_iptc_level1
    result = classify_iptc_level1("Inteligencia artificial y machine learning en la nube")
    assert result == "Technology"


def test_classify_iptc_level1_health():
    from newsradar_api.app.services.keyword_service import classify_iptc_level1
    result = classify_iptc_level1("Vacuna contra la pandemia en el hospital")
    assert result == "Health"


def test_generate_synonyms_returns_list():
    from newsradar_api.app.services.keyword_service import generate_synonyms
    result = generate_synonyms(["test"], max_synonyms=3)
    assert isinstance(result, list)


def test_suggest_synonyms_with_source_empty():
    from newsradar_api.app.services.keyword_service import _suggest_synonyms_with_source
    synonyms, source = _suggest_synonyms_with_source([], max_synonyms=5)
    assert synonyms == []
    assert source == "none"


def test_suggest_synonyms_with_source_no_match():
    from newsradar_api.app.services.keyword_service import _suggest_synonyms_with_source
    synonyms, source = _suggest_synonyms_with_source(["xyqzwvbnm"], max_synonyms=5)
    assert synonyms == []
    assert source == "none"


def test_generate_wordcloud_terms():
    from newsradar_api.app.services.keyword_service import generate_wordcloud_terms
    import asyncio
    texts = ["El gobierno aprobó nuevas leyes de tecnología", "La inteligencia artificial avanza rápido"]
    result = asyncio.run(generate_wordcloud_terms(texts=texts, lang="es", limit=10))
    assert isinstance(result, list)
    if result:
        assert "term" in result[0]
        assert "count" in result[0]


def test_fallback_wordcloud_terms_empty():
    from newsradar_api.app.services.keyword_service import _fallback_wordcloud_terms
    result = _fallback_wordcloud_terms(texts=[], lang="es", limit=10)
    assert result == []


def test_fallback_wordcloud_terms_with_stopwords():
    from newsradar_api.app.services.keyword_service import _fallback_wordcloud_terms
    texts = ["el la y de en por con un una"]
    result = _fallback_wordcloud_terms(texts=texts, lang="es", limit=10)
    assert result == []


def test_normalize_keyword():
    from newsradar_api.app.services.keyword_service import _normalize_keyword
    assert _normalize_keyword("Tecnología") == "tecnologia"
    assert _normalize_keyword("") == ""
    assert _normalize_keyword("  ") == ""
    assert _normalize_keyword(None) == ""
