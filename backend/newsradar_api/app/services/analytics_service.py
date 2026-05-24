from __future__ import annotations

import logging
import unicodedata
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Alert as AlertModel, InformationSource as InformationSourceModel, RSSChannel as RSSChannelModel
from .keyword_service import generate_wordcloud_terms, classify_iptc_level1

logger = logging.getLogger(__name__)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _start_of_day_utc(d: datetime) -> datetime:
    dd = d.astimezone(timezone.utc)
    return datetime(dd.year, dd.month, dd.day, tzinfo=timezone.utc)


def _parse_lang(accept_language: Optional[str]) -> str:
    if not accept_language:
        return "en"
    al = accept_language.lower()
    if al.startswith("es") or ",es" in al:
        return "es"
    return "en"


_DOW_LABELS = {
    "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "es": ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"],
}


def _dow_label(dt: datetime, lang: str) -> str:
    labels = _DOW_LABELS.get(lang) or _DOW_LABELS["en"]
    return labels[dt.weekday()]


_DASH_CATEGORY_LABELS = {
    "en": {"politics": "Politics", "economy": "Economy", "health": "Health", "tech": "Tech"},
    "es": {"politics": "Politica", "economy": "Economia", "health": "Salud", "tech": "Tecnologia"},
}

_IPTC_TO_ES = {
    "Politics": "Politica",
    "Business": "Economia",
    "Health": "Salud",
    "Technology": "Tecnologia",
    "Science": "Ciencia y tecnologia",
    "Sports": "Deporte",
    "Entertainment": "Cultura",
    "Lifestyle": "Estilo de vida y tiempo libre",
    "World": "Internacional",
}


def _dashboard_category_label(key: str, lang: str) -> str:
    return (_DASH_CATEGORY_LABELS.get(lang) or _DASH_CATEGORY_LABELS["en"]).get(key, key)


def _normalize_dashboard_category(value: str) -> str:
    return " ".join((value or "").strip().split())


def _category_key(label: str) -> str:
    return _normalize_dashboard_category(label).lower()


def _news_category_label(raw_category: str, lang: str) -> str:
    value = _normalize_dashboard_category(raw_category)
    if not value:
        return "Sin categoria" if lang == "es" else "Uncategorized"
    return _canonical_dashboard_category(value)


async def _notification_news_stats(mongo_db, start: datetime, start_today: datetime, lang: str) -> Dict[str, Any]:
    start_naive = start.replace(tzinfo=None)
    start_today_naive = start_today.replace(tzinfo=None)
    docs = await mongo_db.notifications.find(
        {"timestamp": {"$gte": start_naive}},
        {"timestamp": 1, "news": 1},
    ).to_list(length=2000)

    total = 0
    today = 0
    by_category: Dict[str, int] = {}
    for doc in docs:
        news_items = doc.get("news") or []
        if not isinstance(news_items, list):
            continue
        ts = doc.get("timestamp")
        is_today = isinstance(ts, datetime) and ts >= start_today_naive
        for item in news_items:
            if not isinstance(item, dict):
                continue
            total += 1
            if is_today:
                today += 1
            label = _news_category_label(item.get("category") or "", lang)
            by_category[label] = by_category.get(label, 0) + 1

    return {"total": total, "today": today, "by_category": by_category}


async def _mongo_news_stats(mongo_db, start: datetime, start_today: datetime, lang: str) -> Dict[str, Any]:
    start_naive = start.replace(tzinfo=None)
    start_today_naive = start_today.replace(tzinfo=None)
    total = await mongo_db.news.count_documents({"created_at": {"$gte": start_naive}})
    today = await mongo_db.news.count_documents({"created_at": {"$gte": start_today_naive}})
    rows = await mongo_db.news.aggregate(
        [
            {"$match": {"created_at": {"$gte": start_naive}}},
            {"$group": {"_id": {"$ifNull": ["$category", "$iptc_category"]}, "count": {"$sum": 1}}},
        ]
    ).to_list(length=100)

    by_category: Dict[str, int] = {}
    for row in rows:
        label = _news_category_label(row.get("_id") or "", lang)
        by_category[label] = by_category.get(label, 0) + int(row.get("count") or 0)

    return {"total": int(total), "today": int(today), "by_category": by_category}


_IPTC_ID_TO_NAME: Dict[int, str] = {
    1000000: "Artes, cultura, entretenimiento y medios",
    2000000: "Policía y justicia",
    3000000: "Catástrofes y accidentes",
    4000000: "Economía, negocios y finanzas",
    5000000: "Educación",
    6000000: "Medio ambiente",
    7000000: "Salud",
    8000000: "Interés humano, animales, insólito",
    9000000: "Mano de obra",
    10000000: "Estilo de vida y tiempo libre",
    11000000: "Política",
    12000000: "Religión y culto",
    13000000: "Ciencia y tecnología",
    14000000: "Sociedad",
    15000000: "Deporte",
    16000000: "Conflicto, guerra y paz",
    17000000: "Meteorología",
}

_RSS_TO_IPTC_NAME: Dict[str, str] = {
    "Politica": "Política",
    "Economia": "Economía, negocios y finanzas",
    "Tecnologia": "Ciencia y tecnología",
    "Deportes": "Deporte",
    "Cultura": "Artes, cultura, entretenimiento y medios",
    "Sociedad": "Sociedad",
    "Internacional": "Conflicto, guerra y paz",
    "Salud": "Salud",
    "Educacion": "Educación",
    "Ciencia": "Ciencia y tecnología",
    "Viajes": "Estilo de vida y tiempo libre",
    "Entretenimiento": "Artes, cultura, entretenimiento y medios",
    "PoliciaJusticia": "Policía y justicia",
    "Catastrofes": "Catástrofes y accidentes",
    "MedioAmbiente": "Medio ambiente",
    "InteresHumano": "Interés humano, animales, insólito",
    "ManoObra": "Mano de obra",
    "Religion": "Religión y culto",
    "Meteorologia": "Meteorología",
}

_IPTC_NAME_TO_RSS: Dict[str, set[str]] = {}
for _rss_cat, _iptc_name in _RSS_TO_IPTC_NAME.items():
    _IPTC_NAME_TO_RSS.setdefault(_iptc_name, set()).add(_rss_cat)

_CLASSIFIER_TO_IPTC_NAME = {
    "Entertainment": _IPTC_ID_TO_NAME[1000000],
    "Business": _IPTC_ID_TO_NAME[4000000],
    "Economy": _IPTC_ID_TO_NAME[4000000],
    "Health": _IPTC_ID_TO_NAME[7000000],
    "Lifestyle": _IPTC_ID_TO_NAME[10000000],
    "Politics": _IPTC_ID_TO_NAME[11000000],
    "Technology": _IPTC_ID_TO_NAME[13000000],
    "Science": _IPTC_ID_TO_NAME[13000000],
    "Sports": _IPTC_ID_TO_NAME[15000000],
    "World": _IPTC_ID_TO_NAME[16000000],
}


def _category_identity(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", _normalize_dashboard_category(value))
    without_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    return without_accents.casefold()


_DASHBOARD_CATEGORY_ALIASES: Dict[str, str] = {
    _category_identity(name): name for name in _IPTC_ID_TO_NAME.values()
}
for _rss_cat, _iptc_name in _RSS_TO_IPTC_NAME.items():
    _DASHBOARD_CATEGORY_ALIASES[_category_identity(_rss_cat)] = _iptc_name
for _classifier_cat, _iptc_name in _CLASSIFIER_TO_IPTC_NAME.items():
    _DASHBOARD_CATEGORY_ALIASES[_category_identity(_classifier_cat)] = _iptc_name


def _canonical_dashboard_category(value: str) -> str:
    label = _normalize_dashboard_category(value)
    return _DASHBOARD_CATEGORY_ALIASES.get(_category_identity(label), label)


def _alert_category_label(category: Dict[str, Any]) -> str:
    category_id = category.get("id")
    if category_id is not None:
        try:
            canonical_name = _IPTC_ID_TO_NAME.get(int(category_id))
        except (TypeError, ValueError):
            canonical_name = None
        if canonical_name:
            return canonical_name
    return _canonical_dashboard_category(category.get("label") or category.get("name") or "")


_CHANNEL_CATEGORY_TO_CLOUD = {
    "politica": "politics",
    "economia": "economy",
    "tecnologia": "technology",
    "deportes": "sports",
    "cultura": "culture",
    "sociedad": "consumption",
    "internacional": "international",
    "salud": "consumption",
    "educacion": "national",
    "ciencia": "technology",
    "viajes": "national",
    "entretenimiento": "entertainment",
    "general": "national",
}


def _map_article_to_cloud_category(a: Dict[str, Any]) -> str:
    iptc = a.get("iptc_category")
    if iptc:
        return _map_iptc_to_cloud_category(iptc)
    raw = a.get("category") or ""
    mapped = _CHANNEL_CATEGORY_TO_CLOUD.get(raw.strip().lower())
    if mapped:
        return mapped
    text = f"{a.get('title', '')} {a.get('description', '')}"
    return _map_iptc_to_cloud_category(classify_iptc_level1(text))


def _map_iptc_to_cloud_category(iptc: str) -> str:
    # Mapeo pragmatico para encajar con las claves que usa el frontend en Nubes.
    v = (iptc or "").strip()
    if v == "Politics":
        return "politics"
    if v == "Business":
        return "economy"
    if v == "Sports":
        return "sports"
    if v == "Entertainment":
        return "entertainment"
    if v == "Technology" or v == "Science":
        return "technology"
    if v == "Health":
        return "consumption"
    if v == "Lifestyle":
        return "culture"
    if v == "World":
        return "international"
    return "national"


def _map_iptc_to_dashboard_category(iptc: str) -> Optional[str]:
    v = (iptc or "").strip()
    if v == "Politics":
        return "politics"
    if v == "Business":
        return "economy"
    if v == "Health":
        return "health"
    if v in ("Technology", "Science"):
        return "tech"
    return None


async def build_dashboard(
    *,
    db: AsyncSession,
    mongo_db,
    days: int,
    accept_language: Optional[str],
) -> Dict[str, Any]:
    """
    Respuesta compatible con el mock de `frontend/src/pages/dashboard/dashboard.jsx`.
    """
    lang = _parse_lang(accept_language)
    now = _now_utc()
    start = now - timedelta(days=max(1, min(days, 90)))
    start_today = _start_of_day_utc(now)

    # Postgres counts
    sources_count = (await db.execute(select(InformationSourceModel))).scalars().all()
    rss_count = (await db.execute(select(RSSChannelModel))).scalars().all()
    alerts_count = (await db.execute(select(AlertModel))).scalars().all()

    # Las noticias visibles para el usuario viven en notifications.news. Si no
    # hay notificaciones, caemos a mongo.news, que es lo que rellena el worker.
    notification_stats = await _notification_news_stats(mongo_db, start, start_today, lang)
    news_stats = notification_stats
    if notification_stats["total"] == 0:
        news_stats = await _mongo_news_stats(mongo_db, start, start_today, lang)

    alert_bucket: Dict[str, int] = {}
    for alert in alerts_count:
        for category in alert.categories or []:
            if not isinstance(category, dict):
                continue
            label = _alert_category_label(category)
            if not label:
                continue
            alert_bucket[label] = alert_bucket.get(label, 0) + 1

    category_names = sorted(
        set(news_stats["by_category"].keys()) | set(alert_bucket.keys()),
        key=lambda name: (-int(news_stats["by_category"].get(name, 0)), name.lower()),
    )
    categorias = [
        {
            "key": _category_key(name),
            "name": name,
            "value": int(news_stats["by_category"].get(name, 0)),
            "alertas": int(alert_bucket.get(name, 0)),
        }
        for name in category_names
    ]

    return {
        "fuentes": {"activas": len(sources_count), "rss": len(rss_count)},
        "noticias": {"hoy": int(news_stats["today"]), "semana": int(news_stats["total"])},
        "alertas": len(alerts_count),
        "evolucion": [],
        "categorias": categorias,
    }


async def build_wordcloud(
    *,
    db: AsyncSession,
    user_id: int,
    mongo_db,
    days: int,
    limit: int,
    accept_language: Optional[str],
    cloud_category: Optional[str],
    cache_max_age_hours: int = 1,
) -> List[Dict[str, Any]]:
    """
    Devuelve [{term, count}] para nube global o por categoria.
    Lee de notifications.news (única colección poblada por el daemon).
    Se cachea en Mongo en `wordcloud_cache`.
    """
    lang = _parse_lang(accept_language)
    now = _now_utc()
    start = now - timedelta(days=max(1, min(days, 90)))

    user_alerts = (
        await db.execute(select(AlertModel).where(AlertModel.user_id == user_id))
    ).scalars().all()
    alert_ids = [int(a.id) for a in user_alerts]

    if not alert_ids:
        return []

    cache_key = {
        "scope": "category" if cloud_category else "global",
        "category": cloud_category,
        "user_id": int(user_id),
        "days": int(days),
        "limit": int(limit),
        "lang": lang,
    }

    cached = await mongo_db.wordcloud_cache.find_one(cache_key)
    if cached and isinstance(cached.get("updated_at"), datetime) and cached.get("terms"):
        age = now - cached["updated_at"].astimezone(timezone.utc)
        if age.total_seconds() <= cache_max_age_hours * 3600:
            return cached["terms"]

    notif_docs = await mongo_db.notifications.find(
        {"alert_id": {"$in": alert_ids}, "timestamp": {"$gte": start}},
        {"news": 1},
    ).sort("timestamp", -1).to_list(length=200)

    if not notif_docs:
        news_docs = await mongo_db.news.find(
            {"alert_id": {"$in": alert_ids}, "created_at": {"$gte": start}},
        ).sort("created_at", -1).to_list(length=200)
        if news_docs:
            notif_docs = [{"news": news_docs}]

    articles: List[Dict[str, Any]] = []
    for nd in notif_docs:
        for item in nd.get("news") or []:
            articles.append(item)
            if len(articles) >= 200:
                break
        if len(articles) >= 200:
            break

    texts: List[str] = []
    for a in articles:
        if cloud_category:
            if cloud_category.isdigit():
                category_id = int(cloud_category)
                iptc_name = _IPTC_ID_TO_NAME.get(category_id)
                rss_cats = _IPTC_NAME_TO_RSS.get(iptc_name) if iptc_name else None
                if rss_cats:
                    if a.get("category", "").strip() not in rss_cats:
                        continue
                else:
                    continue
            elif _map_article_to_cloud_category(a) != cloud_category:
                continue
        title = (a.get("title") or "").strip()
        desc = (a.get("description") or "").strip()
        if title or desc:
            texts.append(f"{title}\n{desc}".strip())

    if not texts:
        return []

    try:
        terms = await generate_wordcloud_terms(texts=texts, lang=lang, limit=limit)
    except Exception as e:
        logger.error("Error generando wordcloud con IA: %s", str(e))
        terms = []

    await mongo_db.wordcloud_cache.update_one(
        cache_key,
        {"$set": {**cache_key, "terms": terms, "updated_at": now}},
        upsert=True,
    )
    return terms
