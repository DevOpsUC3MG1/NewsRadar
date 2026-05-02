from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Alert as AlertModel, InformationSource as InformationSourceModel, RSSChannel as RSSChannelModel
from .ia_service import generate_wordcloud_terms

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


def _dashboard_category_label(key: str, lang: str) -> str:
    return (_DASH_CATEGORY_LABELS.get(lang) or _DASH_CATEGORY_LABELS["en"]).get(key, key)


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

    # Mongo counts
    news_today = await mongo_db.news.count_documents({"created_at": {"$gte": start_today.replace(tzinfo=None)}})
    news_period = await mongo_db.news.count_documents({"created_at": {"$gte": start.replace(tzinfo=None)}})

    # Evolution: news per day (last N days)
    # created_at se guarda como naive UTC en rss_worker -> comparamos con naive UTC.
    pipeline = [
        {"$match": {"created_at": {"$gte": start.replace(tzinfo=None)}}},
        {
            "$group": {
                "_id": {
                    "y": {"$year": "$created_at"},
                    "m": {"$month": "$created_at"},
                    "d": {"$dayOfMonth": "$created_at"},
                },
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id.y": 1, "_id.m": 1, "_id.d": 1}},
    ]
    rows = await mongo_db.news.aggregate(pipeline).to_list(length=500)

    # Relleno de dias faltantes
    by_day: Dict[str, int] = {}
    for r in rows:
        _id = r.get("_id") or {}
        y, m, d = _id.get("y"), _id.get("m"), _id.get("d")
        if not (y and m and d):
            continue
        key = f"{y:04d}-{m:02d}-{d:02d}"
        by_day[key] = int(r.get("count") or 0)

    evolution: List[Dict[str, Any]] = []
    cur = _start_of_day_utc(start)
    end = _start_of_day_utc(now)
    while cur <= end:
        key = cur.strftime("%Y-%m-%d")
        evolution.append({"name": _dow_label(cur, lang), "date": key, "noticias": by_day.get(key, 0)})
        cur += timedelta(days=1)

    # Categories (4 buckets) from iptc_category
    cat_pipeline = [
        {"$match": {"created_at": {"$gte": start.replace(tzinfo=None)}}},
        {"$group": {"_id": "$iptc_category", "count": {"$sum": 1}}},
    ]
    cat_rows = await mongo_db.news.aggregate(cat_pipeline).to_list(length=50)
    bucket = {"politics": 0, "economy": 0, "health": 0, "tech": 0}
    for r in cat_rows:
        key = _map_iptc_to_dashboard_category(r.get("_id") or "")
        if not key:
            continue
        bucket[key] += int(r.get("count") or 0)

    categorias = [
        {"key": k, "name": _dashboard_category_label(k, lang), "value": v} for k, v in bucket.items()
    ]

    return {
        "fuentes": {"activas": len(sources_count), "rss": len(rss_count)},
        "noticias": {"hoy": int(news_today), "semana": int(news_period)},
        "alertas": len(alerts_count),
        "evolucion": evolution[-max(1, min(days, 90)) :],
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
    if cached and isinstance(cached.get("updated_at"), datetime):
        age = now - cached["updated_at"].astimezone(timezone.utc)
        if age.total_seconds() <= cache_max_age_hours * 3600:
            terms = cached.get("terms") or []
            if isinstance(terms, list):
                return terms

    match: Dict[str, Any] = {
        "created_at": {"$gte": start.replace(tzinfo=None)},
        "alert_id": {"$in": alert_ids},
    }
    if cloud_category:
        # Filtramos por iptc->cloud category
        # Guardamos iptc_category en news; filtramos por un set equivalente.
        # Como el mapping no es 1:1, hacemos filtro por iptc_category y mapeamos en python.
        pass

    docs = await mongo_db.news.find(match, {"title": 1, "description": 1, "iptc_category": 1}).sort(
        "created_at", -1
    ).limit(200).to_list(length=200)

    texts: List[str] = []
    for d in docs:
        if cloud_category:
            mapped = _map_iptc_to_cloud_category(d.get("iptc_category") or "")
            if mapped != cloud_category:
                continue
        title = (d.get("title") or "").strip()
        desc = (d.get("description") or "").strip()
        if title or desc:
            texts.append(f"{title}\n{desc}".strip())

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
