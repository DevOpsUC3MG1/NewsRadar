"""
Servicio de IA para:
- Generación de sinónimos (diccionario de palabras clave)
- Clasificación IPTC (nivel 1)

RNF-06: Trazabilidad de prompts IA
- Todos los prompts utilizados están documentados en PROMPTS.md
- Proveedor/modelo configurables por variables de entorno
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuración IA
# ---------------------------------------------------------------------------
# IA_PROVIDER: "gemini" | "openai" (si está vacío se autodetecta)
IA_PROVIDER = (os.getenv("IA_PROVIDER") or "").strip().lower()

# Google AI Studio / Gemini Developer API (Generative Language API)
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# OpenAI (legacy / opcional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

_openai_client = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI  # type: ignore

        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        logger.warning("OpenAI client no disponible (%s). Se ignorara.", str(e))


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _effective_provider() -> str:
    if IA_PROVIDER in ("gemini", "openai"):
        return IA_PROVIDER
    if GEMINI_API_KEY:
        return "gemini"
    if _openai_client:
        return "openai"
    return "none"


def _gemini_generate_text(*, prompt: str, temperature: float, max_output_tokens: int) -> Optional[str]:
    """
    Llama a Gemini via Generative Language API (Gemini Developer API).
    Implementado con stdlib (urllib) para evitar dependencias extra.
    """
    if not GEMINI_API_KEY:
        return None

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload: Dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_output_tokens},
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw)
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8")
        except Exception:
            body = "<no-body>"
        logger.error("Gemini HTTPError %s: %s", e.code, body)
        return None
    except Exception as e:
        logger.error("Error llamando a Gemini: %s", str(e))
        return None

    try:
        candidates = data.get("candidates") or []
        content = candidates[0].get("content") if candidates else None
        parts = (content or {}).get("parts") or []
        text = parts[0].get("text") if parts else None
        return (text or "").strip() or None
    except Exception:
        logger.error("Respuesta Gemini inesperada: %s", data)
        return None


def _openai_generate_text(*, system: str, user: str, temperature: float, max_tokens: int) -> Optional[str]:
    if not _openai_client:
        return None
    try:
        response = _openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error("Error llamando a OpenAI: %s", str(e))
        return None


# ---------------------------------------------------------------------------
# Prompts (RNF-06)
# ---------------------------------------------------------------------------

def generate_synonyms(keywords: List[str], max_synonyms: int = 5) -> List[str]:
    """
    PROMPT_ID: IA-001-SYNONYMS
    Descripción: Generación de sinónimos para descriptores de alertas
    """
    provider = _effective_provider()
    if provider == "none":
        logger.warning("IA no configurada (GOOGLE_API_KEY/GEMINI_API_KEY u OPENAI_API_KEY).")
        return []

    base = [k.strip() for k in (keywords or []) if isinstance(k, str) and k.strip()]
    if not base:
        return []

    keywords_str = ", ".join(base)
    prompt = f"""
Eres un asistente especializado en generación de palabras clave relacionadas para motores de búsqueda de noticias.

Dadas estas palabras clave: {keywords_str}

Genera entre 3 y 10 sinónimos o palabras relacionadas que podrían mejorar la búsqueda y captura de noticias relevantes.
Las palabras deben ser:
- En español
- Relevantes al tema
- Que amplíen la cobertura sin ser demasiado genéricas
- Separadas por comas

Responde SOLO con las palabras, sin explicación adicional.
Ejemplo de respuesta: "economía digital, transformación digital, negocio electrónico"
""".strip()

    if provider == "gemini":
        text = _gemini_generate_text(prompt=prompt, temperature=0.7, max_output_tokens=150) or ""
    else:
        text = (
            _openai_generate_text(
                system="Eres un asistente experto en generación de palabras clave para búsqueda de noticias.",
                user=prompt,
                temperature=0.7,
                max_tokens=150,
            )
            or ""
        )

    synonyms = [s.strip() for s in text.split(",") if s.strip()]
    logger.info("Sinónimos generados para %s: %s", keywords_str, synonyms)
    return synonyms[:max_synonyms]


def classify_iptc_level1(text: str) -> str:
    """
    PROMPT_ID: IA-002-IPTC-CLASSIFICATION
    Descripción: Clasificación automática de noticias en categorías IPTC nivel 1
    """
    provider = _effective_provider()
    if provider == "none":
        logger.warning("IA no configurada. Devolviendo 'General'.")
        return "General"

    if not text or len(text.strip()) < 10:
        return "General"

    prompt = f"""
Clasifica el siguiente texto en UNA ÚNICA categoría IPTC de nivel 1.

Categorías disponibles:
- Politics
- Business
- Sports
- Entertainment
- Science
- Technology
- Health
- Lifestyle
- World
- General

Texto a clasificar:
{text[:500]}

Responde SOLO con el nombre de la categoría, sin explicación.
""".strip()

    if provider == "gemini":
        category = _gemini_generate_text(prompt=prompt, temperature=0.3, max_output_tokens=50) or "General"
    else:
        category = (
            _openai_generate_text(
                system="Eres un clasificador experto de noticias en categorías IPTC nivel 1.",
                user=prompt,
                temperature=0.3,
                max_tokens=50,
            )
            or "General"
        )

    category = (category or "General").strip()
    logger.info("Categoría IPTC asignada: %s", category)
    return category


# ---------------------------------------------------------------------------
# Keyword dictionary (MongoDB) para cachear sinónimos
# ---------------------------------------------------------------------------

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
    """
    Devuelve keywords ampliadas usando el diccionario cacheado (y generando si falta).
    """
    base = [k.strip() for k in (keywords or []) if isinstance(k, str) and k.strip()]
    if not base:
        return []

    provider = _effective_provider()
    out: List[str] = []
    seen = set()

    for kw in base:
        low_kw = kw.lower()
        if low_kw not in seen:
            seen.add(low_kw)
            out.append(kw)

        cached = await get_cached_synonyms(mongo_db, keyword=kw, max_age_days=max_age_days)
        if not cached and provider != "none":
            generated = await asyncio.to_thread(generate_synonyms, [kw], max_synonyms_per_keyword)
            cached = generated or []
            if cached:
                await upsert_synonyms(mongo_db, keyword=kw, synonyms=cached, provider=provider)

        for syn in cached[:max_synonyms_per_keyword]:
            low = syn.lower()
            if low in seen:
                continue
            seen.add(low)
            out.append(syn)

    return out

