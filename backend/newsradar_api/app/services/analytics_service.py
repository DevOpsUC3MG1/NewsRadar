from __future__ import annotations

import logging
import os
import unicodedata
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Alert as AlertModel, InformationSource as InformationSourceModel, RSSChannel as RSSChannelModel
from .keyword_service import generate_wordcloud_terms

logger = logging.getLogger(__name__)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _start_of_day_utc(d: datetime) -> datetime:
    dd = d.astimezone(timezone.utc)
    return datetime(dd.year, dd.month, dd.day, tzinfo=timezone.utc)


def _parse_lang(accept_language: Optional[str]) -> str:
    if os.getenv("FEATURE_FLAG_BILINGUAL", "true").lower() == "false":
        return "en"
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
    if lang == "es":
        return _IPTC_TO_ES.get(value, value)
    return value


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
            {"$group": {"_id": "$iptc_category", "count": {"$sum": 1}}},
        ]
    ).to_list(length=100)

    by_category: Dict[str, int] = {}
    for row in rows:
        label = _news_category_label(row.get("_id") or "", lang)
        by_category[label] = by_category.get(label, 0) + int(row.get("count") or 0)

    return {"total": int(total), "today": int(today), "by_category": by_category}


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


def _alert_category_to_cloud_slug(label: str) -> str:
    if not label:
        return "national"
    normalized = unicodedata.normalize("NFD", label)
    normalized = "".join(c for c in normalized if unicodedata.category(c) != "Mn")
    mapping = {
        "Artes, cultura, entretenimiento y medios": "culture",
        "Policia y justicia": "national",
        "Catastrofes y accidentes": "national",
        "Economia, negocios y finanzas": "economy",
        "Educacion": "education",
        "Medio ambiente": "national",
        "Salud": "health",
        "Interes humano, animales, insolito": "national",
        "Mano de obra": "national",
        "Estilo de vida y tiempo libre": "culture",
        "Politica": "politics",
        "Religion y culto": "national",
        "Ciencia y tecnologia": "technology",
        "Sociedad": "society",
        "Deporte": "sports",
        "Conflicto, guerra y paz": "national",
        "Meteorologia": "national",
    }
    return mapping.get(normalized, "national")


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
            label = _normalize_dashboard_category(category.get("label") or category.get("name") or "")
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
    cache_max_age_hours: int = 6,
) -> List[Dict[str, Any]]:
    """
    Devuelve [{term, count}] para nube global o por categoria.
    Lee de notifications.news (única colección poblada por el daemon).
    Se cachea en Mongo en `wordcloud_cache`.
    """
    if os.getenv("FEATURE_FLAG_WORDCLOUD", "true").lower() == "false":
        raise HTTPException(status_code=503, detail="Wordcloud feature disabled")
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
        "version": 2,
        "scope": "category" if cloud_category else "global",
        "category": cloud_category,
        "user_id": int(user_id),
        "days": int(days),
        "limit": int(limit),
        "lang": lang,
    }

    cached = await mongo_db.wordcloud_cache.find_one(cache_key)
    if cached and isinstance(cached.get("updated_at"), datetime):
        age = now - cached["updated_at"].astimezone(timezone.utc)
        if age.total_seconds() <= cache_max_age_hours * 3600:
            terms = cached.get("terms") or []
            if isinstance(terms, list):
                return terms

    alert_slugs: Dict[int, Set[str]] = {}
    for alert in user_alerts:
        slugs = set()
        for cat in alert.categories or []:
            label = cat.get("label") or cat.get("name") or ""
            slug = _alert_category_to_cloud_slug(label)
            slugs.add(slug)
        alert_slugs[int(alert.id)] = slugs

    notif_docs = await mongo_db.notifications.find(
        {"alert_id": {"$in": alert_ids}, "timestamp": {"$gte": start}},
        {"news": 1},
    ).sort("timestamp", -1).to_list(length=200)

    texts: List[str] = []
    for nd in notif_docs:
        if cloud_category:
            nd_slugs = alert_slugs.get(nd.get("alert_id"), set())
            if cloud_category not in nd_slugs:
                continue
        for item in nd.get("news") or []:
            title = (item.get("title") or "").strip()
            desc = (item.get("description") or "").strip()
            if title or desc:
                texts.append(f"{title}\n{desc}".strip())
            if len(texts) >= 200:
                break
        if len(texts) >= 200:
            break

    if not texts:
        await mongo_db.wordcloud_cache.update_one(
            cache_key,
            {"$set": {**cache_key, "terms": [], "updated_at": now}},
            upsert=True,
        )
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
