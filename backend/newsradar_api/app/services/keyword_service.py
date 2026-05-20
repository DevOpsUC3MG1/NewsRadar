"""
Servicios deterministas para:
- Generación manual de sinónimos
- Clasificación IPTC por reglas
- Wordcloud por frecuencia
"""

from __future__ import annotations

import json
import logging
import os
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=str(_env_path) if _env_path.exists() else None)


def _find_project_root() -> Path:
    start = Path(__file__).resolve()
    for parent in start.parents:
        candidate = parent / "data" / "manual_synonyms.json"
        if candidate.exists():
            return parent
    return start.parents[4]


_PROJECT_ROOT = _find_project_root()
_DEFAULT_SYNONYMS = str(_PROJECT_ROOT / "data" / "manual_synonyms.json")

_raw = os.getenv("MANUAL_SYNONYMS_FILE")
if _raw:
    MANUAL_SYNONYMS_FILE = str((_PROJECT_ROOT / _raw).resolve())
    if not os.path.exists(MANUAL_SYNONYMS_FILE):
        logger.warning("MANUAL_SYNONYMS_FILE not found at '%s' (from env var '%s'), falling back to '%s'",
                       MANUAL_SYNONYMS_FILE, _raw, _DEFAULT_SYNONYMS)
        MANUAL_SYNONYMS_FILE = _DEFAULT_SYNONYMS
else:
    MANUAL_SYNONYMS_FILE = _DEFAULT_SYNONYMS
_MANUAL_SYNONYMS_CACHE: Optional[Dict[str, List[str]]] = None

_WORD_RE = re.compile(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9_-]{2,}")
_STOPWORDS = {
    "es": {
        "ante", "bajo", "cada", "como", "con", "contra", "cual", "cuando", "de", "del", "desde", "donde",
        "durante", "el", "ella", "ellas", "ellos", "en", "entre", "era", "esta", "este", "estos", "estas",
        "fue", "han", "hasta", "hay", "hoy", "la", "las", "le", "les", "lo", "los", "mas", "muy", "noticia",
        "noticias", "para", "pero", "por", "que", "quien", "se", "segun", "ser", "sin", "sobre", "son", "sus",
        "tras", "una", "uno", "unos", "unas", "video",
    },
    "en": {
        "about", "after", "also", "and", "are", "been", "but", "for", "from", "have", "into", "its", "more",
        "news", "not", "that", "the", "their", "them", "there", "these", "they", "this", "those", "today",
        "under", "video", "was", "were", "what", "when", "with", "would", "your",
    },
}
_IPTC_RULES = {
    "Politics": (
        "gobierno", "parlamento", "congreso", "senado", "elecciones", "politica", "presidente", "ministro",
        "legislativo", "ejecutivo", "presupuesto", "diplomacia", "geopolitica",
    ),
    "Business": (
        "empresa", "mercado", "bolsa", "ibex", "acciones", "inversion", "inflacion", "banco", "finanzas",
        "economia", "tipos de interes", "ingresos", "beneficio", "startup", "retail",
    ),
    "Sports": (
        "futbol", "deporte", "liga", "champions", "tenis", "baloncesto", "formula 1", "carrera", "gol",
        "partido", "torneo", "real madrid", "barcelona",
    ),
    "Entertainment": (
        "cine", "serie", "streaming", "musica", "festival", "pelicula", "actor", "actriz", "television",
        "netflix", "concierto",
    ),
    "Science": (
        "investigacion", "ciencia", "cientifico", "laboratorio", "descubrimiento", "estudio", "universidad",
        "ensayo clinico", "experimento",
    ),
    "Technology": (
        "tecnologia", "software", "hardware", "inteligencia artificial", "machine learning", "big data",
        "semiconductores", "ciberseguridad", "nube", "cloud", "aplicacion", "algoritmo", "blockchain",
    ),
    "Health": (
        "salud", "sanidad", "hospital", "vacuna", "medicina", "medico", "medica", "paciente", "pandemia",
        "diagnostico", "atencion sanitaria",
    ),
    "Lifestyle": (
        "turismo", "viajes", "vivienda", "consumo", "gastronomia", "moda", "bienestar", "hogar",
    ),
    "World": (
        "guerra", "ucrania", "rusia", "eeuu", "china", "otan", "internacional", "conflicto", "onu",
        "oriente medio", "union europea",
    ),
}


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_keyword(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_like = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    lowered = ascii_like.lower()
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return " ".join(lowered.split())


def _load_manual_synonyms() -> Dict[str, List[str]]:
    global _MANUAL_SYNONYMS_CACHE
    if _MANUAL_SYNONYMS_CACHE is not None:
        return _MANUAL_SYNONYMS_CACHE

    try:
        with open(MANUAL_SYNONYMS_FILE, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except FileNotFoundError:
        logger.info("No se encontro diccionario manual de sinonimos en %s", MANUAL_SYNONYMS_FILE)
        _MANUAL_SYNONYMS_CACHE = {}
        return _MANUAL_SYNONYMS_CACHE
    except Exception as exc:
        logger.warning("No se pudo cargar el diccionario manual de sinonimos: %s", exc)
        _MANUAL_SYNONYMS_CACHE = {}
        return _MANUAL_SYNONYMS_CACHE

    if not isinstance(raw, dict):
        logger.warning("El diccionario manual de sinonimos debe ser un objeto JSON.")
        _MANUAL_SYNONYMS_CACHE = {}
        return _MANUAL_SYNONYMS_CACHE

    normalized_map: Dict[str, List[str]] = {}
    for key, values in raw.items():
        if not isinstance(key, str) or not isinstance(values, list):
            continue
        normalized_key = _normalize_keyword(key)
        if not normalized_key:
            continue
        clean_values = [item.strip() for item in values if isinstance(item, str) and item.strip()]
        if clean_values:
            normalized_map[normalized_key] = clean_values

    _MANUAL_SYNONYMS_CACHE = normalized_map
    return _MANUAL_SYNONYMS_CACHE


def _manual_synonyms_for_keywords(keywords: List[str], max_synonyms: int) -> List[str]:
    dictionary = _load_manual_synonyms()
    if not dictionary:
        return []

    results: List[str] = []
    seen = set()

    for keyword in keywords:
        normalized_keyword = _normalize_keyword(keyword)
        if not normalized_keyword:
            continue

        candidates: List[str] = []
        exact = dictionary.get(normalized_keyword) or []
        if exact:
            candidates.extend(exact)
        else:
            for token in normalized_keyword.split():
                candidates.extend(dictionary.get(token) or [])

        for candidate in candidates:
            normalized_candidate = _normalize_keyword(candidate)
            if not normalized_candidate or normalized_candidate == normalized_keyword or normalized_candidate in seen:
                continue
            seen.add(normalized_candidate)
            results.append(candidate.strip())
            if len(results) >= max_synonyms:
                return results

    return results


def _fallback_wordcloud_terms(*, texts: List[str], lang: str, limit: int) -> List[Dict[str, Any]]:
    language = "es" if (lang or "").lower().startswith("es") else "en"
    stopwords = _STOPWORDS[language]
    counts: Counter[str] = Counter()

    for text in texts[:200]:
        seen_in_text = set()
        for raw in _WORD_RE.findall(text or ""):
            word = raw.strip("-_").lower()
            if len(word) < 3 or word.isdigit() or word in stopwords:
                continue
            seen_in_text.add(word)
        counts.update(seen_in_text)

    if not counts:
        return []

    most_common = counts.most_common(limit)
    max_count = most_common[0][1]
    return [
        {"term": term.upper(), "count": max(1, min(100, round((freq / max_count) * 100)))}
        for term, freq in most_common
    ]


def _suggest_synonyms_with_source(keywords: List[str], max_synonyms: int = 5) -> tuple[List[str], str]:
    base = [k.strip() for k in (keywords or []) if isinstance(k, str) and k.strip()]
    if not base:
        return [], "none"

    max_synonyms = max(1, int(max_synonyms))
    synonyms = _manual_synonyms_for_keywords(base, max_synonyms)
    if synonyms:
        logger.info("Sinónimos manuales para %s: %s", ", ".join(base), synonyms)
        return synonyms[:max_synonyms], "manual"

    logger.info("No hay sinónimos manuales para %s en %s", ", ".join(base), MANUAL_SYNONYMS_FILE)
    return [], "none"


def generate_synonyms(keywords: List[str], max_synonyms: int = 5) -> List[str]:
    synonyms, _ = _suggest_synonyms_with_source(keywords, max_synonyms)
    return synonyms


def classify_iptc_level1(text: str) -> str:
    if not text or len(text.strip()) < 10:
        return "General"

    normalized_text = _normalize_keyword(text)
    if not normalized_text:
        return "General"

    best_category = "General"
    best_score = 0
    for category, hints in _IPTC_RULES.items():
        score = sum(1 for hint in hints if hint in normalized_text)
        if score > best_score:
            best_score = score
            best_category = category

    return best_category


async def generate_wordcloud_terms(*, texts: List[str], lang: str, limit: int = 20) -> List[Dict[str, Any]]:
    limit = max(5, min(int(limit), 50))
    return _fallback_wordcloud_terms(texts=texts, lang=lang, limit=limit)


async def get_cached_synonyms(
    mongo_db,
    *,
    keyword: str,
    max_age_days: int = 30,
) -> List[str]:
    if not keyword:
        return []

    doc = await mongo_db.keyword_dictionary.find_one({"keyword": keyword})
    if not doc:
        return []

    updated_at = doc.get("updated_at")
    if isinstance(updated_at, datetime):
        age = _now_utc() - updated_at.astimezone(timezone.utc)
        if age.days > max_age_days:
            return []

    synonyms = doc.get("synonyms") or []
    return [s.strip() for s in synonyms if isinstance(s, str) and s.strip()]


async def upsert_synonyms(
    mongo_db,
    *,
    keyword: str,
    synonyms: List[str],
    provider: str,
) -> None:
    if not keyword:
        return

    clean: List[str] = []
    seen = set()
    for s in synonyms or []:
        if not isinstance(s, str):
            continue
        t = s.strip()
        if not t:
            continue
        low = t.lower()
        if low in seen:
            continue
        seen.add(low)
        clean.append(t)

    await mongo_db.keyword_dictionary.update_one(
        {"keyword": keyword},
        {"$set": {"keyword": keyword, "synonyms": clean, "provider": provider, "updated_at": _now_utc()}},
        upsert=True,
    )


async def expand_keywords(
    mongo_db,
    *,
    keywords: List[str],
    max_synonyms_per_keyword: int = 5,
    max_age_days: int = 30,
) -> List[str]:
    base = [k.strip() for k in (keywords or []) if isinstance(k, str) and k.strip()]
    if not base:
        return []

    out: List[str] = []
    seen = set()

    for kw in base:
        low_kw = kw.lower()
        if low_kw not in seen:
            seen.add(low_kw)
            out.append(kw)

        cached = await get_cached_synonyms(mongo_db, keyword=kw, max_age_days=max_age_days)
        if not cached:
            generated, source = _suggest_synonyms_with_source([kw], max_synonyms_per_keyword)
            cached = generated or []
            if cached:
                await upsert_synonyms(mongo_db, keyword=kw, synonyms=cached, provider=source)

        for syn in cached[:max_synonyms_per_keyword]:
            low = syn.lower()
            if low in seen:
                continue
            seen.add(low)
            out.append(syn)

    return out
