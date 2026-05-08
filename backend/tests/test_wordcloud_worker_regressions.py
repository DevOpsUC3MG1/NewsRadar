import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.append(str(Path(__file__).resolve().parents[1]))

from newsradar_api.app.services.keyword_service import generate_synonyms, generate_wordcloud_terms
from newsradar_api.app.services.rss_worker import RSSWorker


class _FakeExecuteResult:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self):
        return self

    def all(self):
        return self._rows


class _FakeSession:
    def __init__(self, categories=None, channels=None):
        self._categories = categories or []
        self._channels = channels or []
        self.calls = 0

    async def execute(self, _query):
        self.calls += 1
        rows = self._categories if self.calls == 1 else self._channels
        return _FakeExecuteResult(rows)


def test_generate_wordcloud_terms_uses_deterministic_fallback():
    result = asyncio.run(
        generate_wordcloud_terms(
            texts=[
                "La inteligencia artificial avanza en salud y tecnologia",
                "La tecnologia aplicada a salud mejora diagnosticos con inteligencia artificial",
            ],
            lang="es",
            limit=5,
        )
    )

    assert result
    assert all("term" in item and "count" in item for item in result)
    assert any(item["term"] in {"INTELIGENCIA", "ARTIFICIAL", "TECNOLOGIA", "SALUD"} for item in result)


def test_generate_synonyms_uses_manual_dictionary():
    result = generate_synonyms(["inteligencia artificial"], max_synonyms=5)

    assert result
    assert "IA" in result
    assert "aprendizaje automatico" in result


def test_get_alert_channels_accepts_code_label_categories():
    categories = [SimpleNamespace(id=3, name="Tecnologia")]
    channels = [SimpleNamespace(id=9, category_id=3)]
    session = _FakeSession(categories=categories, channels=channels)
    worker = RSSWorker(db=session, mongo_db=None)
    alert = SimpleNamespace(
        categories=[{"code": "technology", "label": "Tecnologia"}],
        rss_channels_ids=[],
    )

    result = asyncio.run(worker._get_alert_channels(alert))

    assert [channel.id for channel in result] == [9]
