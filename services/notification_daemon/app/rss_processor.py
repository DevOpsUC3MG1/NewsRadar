"""
Procesador de feeds RSS y matching contra alertas.

Descarga RSS, parsea entradas y filtra por:
  - descriptor (palabra clave en título/descripción) OR
  - categoría (la del canal RSS)

Solo se consideran noticias publicadas DESDE la última ejecución de la alerta.
"""
from __future__ import annotations
from zoneinfo import ZoneInfo
import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    """Una noticia extraída de un feed RSS."""
    title: str
    link: str
    summary: str
    published: datetime | None
    source_name: str
    channel_url: str
    channel_category: str  # categoría del canal en rss_sources.json (p.ej. "Politica")
    guid: str = ""
    matched_descriptors: list[str] = field(default_factory=list)
    matched_category: str | None = None


def _parse_date(entry: dict) -> datetime | None:
    """Intenta extraer la fecha de publicación del entry, devolviéndola en UTC."""
    # fallback a parseo manual
    for key in ("published", "updated"):
        raw = entry.get(key)
        if raw:
            try:
                dt = parsedate_to_datetime(raw)
                print(f"Parsed date '{raw}' -> {dt} (tzinfo={dt.tzinfo})")
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=ZoneInfo("Europe/Madrid"))
                    print(f"Assuming timezone Europe/Madrid -> {dt} (tzinfo={dt.tzinfo})")
                return dt.astimezone(timezone.utc)
            except (TypeError, ValueError):
                pass

    # feedparser ya rellena published_parsed/updated_parsed si puede
    for key in ("published_parsed", "updated_parsed"):
        struct = entry.get(key)
        if struct:
            try:
                return datetime(*struct[:6], tzinfo=timezone.utc)
            except (TypeError, ValueError):
                pass

    return None


async def fetch_feed(
    client: httpx.AsyncClient,
    url: str,
    timeout: float = 20.0,
) -> str | None:
    """Descarga el contenido de un feed. Devuelve None si falla."""
    try:
        resp = await client.get(url, timeout=timeout, follow_redirects=True)
        resp.raise_for_status()
        return resp.text
    except (httpx.HTTPError, httpx.TimeoutException) as e:
        logger.warning("Error descargando %s: %s", url, e)
        return None


def parse_feed(
    raw_xml: str,
    source_name: str,
    channel_url: str,
    channel_category: str,
    since: datetime | None,
) -> list[NewsItem]:
    """Parsea el XML y devuelve solo las noticias publicadas DESDE `since`."""
    parsed = feedparser.parse(raw_xml)
    items: list[NewsItem] = []
    for entry in parsed.entries:
        pub = _parse_date(entry)
        if since is not None and pub is not None and pub <= since:
            continue
        # si no hay fecha y tenemos un `since`, descartamos para evitar duplicados
        if since is not None and pub is None:
            continue

        items.append(NewsItem(
            title=(entry.get("title") or "").strip(),
            link=(entry.get("link") or "").strip(),
            summary=_strip_html(entry.get("summary") or entry.get("description") or ""),
            published=pub,
            source_name=source_name,
            channel_url=channel_url,
            channel_category=channel_category,
            guid=(entry.get("id") or entry.get("link") or "").strip(),
        ))
    return items


_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    """Quita tags HTML básicos del summary."""
    if not text:
        return ""
    return _TAG_RE.sub("", text).strip()


def _normalize(s: str) -> str:
    """Lowercase + sin acentos básicos para matching insensible."""
    s = s.lower()
    repl = str.maketrans("áéíóúüñ", "aeiouun")
    return s.translate(repl)


def matches_alert(
    item: NewsItem,
    descriptors: list[str],
    category_codes: list[str],
) -> bool:
    """Devuelve True si la noticia matchea por descriptor O categoría.

    - descriptor: palabra/frase que aparece en title o summary
      (búsqueda como subcadena, normalizada y sensible a límite de palabra
      para evitar falsos positivos como "Ibex" dentro de "exhibe").
    - category_codes: lista de códigos de categoría (p.ej. "politica").
      Match si la categoría del canal coincide con alguno (case-insensitive).
    """
    # category match
    if category_codes:
        ch_cat = _normalize(item.channel_category)
        for code in category_codes:
            if _normalize(code) == ch_cat:
                item.matched_category = item.channel_category
                # no return: queremos también guardar matched_descriptors si los hay
                break

    # descriptor match: usamos word boundaries para evitar false positives
    if descriptors:
        haystack = _normalize(f"{item.title} {item.summary}")
        for desc in descriptors:
            d = _normalize(desc).strip()
            if not d:
                continue
            # word boundary para palabras simples; subcadena para frases con espacios
            if " " in d:
                if d in haystack:
                    item.matched_descriptors.append(desc)
            else:
                if re.search(rf"\b{re.escape(d)}\b", haystack):
                    item.matched_descriptors.append(desc)

    return bool(item.matched_descriptors) or item.matched_category is not None


async def gather_news(
    channels: list[dict],
    since: datetime | None,
) -> list[NewsItem]:
    """Descarga y parsea en paralelo todos los canales indicados.

    `channels` es una lista de dicts con: source_name, url, category.
    """
    # Algunos sitios (El País, etc.) bloquean User-Agents que no parecen navegador.
    # Usamos un UA estándar; los feeds RSS son públicos por diseño.
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; NewsRadar/1.0; +https://newsradar.com/bot) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        ),
        "Accept": (
            "application/rss+xml, application/atom+xml, application/xml;q=0.9, "
            "text/xml;q=0.8, */*;q=0.5"
        ),
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }
    async with httpx.AsyncClient(headers=headers) as client:
        tasks = [fetch_feed(client, ch["url"]) for ch in channels]
        raws = await asyncio.gather(*tasks, return_exceptions=False)

    all_items: list[NewsItem] = []
    for ch, raw in zip(channels, raws):
        if not raw:
            continue
        try:
            items = parse_feed(
                raw,
                source_name=ch["source_name"],
                channel_url=ch["url"],
                channel_category=ch["category"],
                since=since,
            )
            all_items.extend(items)
        except Exception as e:  # parser muy permisivo, raro pero posible
            logger.warning("Error parseando %s: %s", ch["url"], e)

    return all_items
