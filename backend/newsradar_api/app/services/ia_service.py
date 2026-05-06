"""
Servicio de IA para:
- Generación de sinónimos (diccionario de palabras clave)
- Clasificación IPTC (nivel 1)

RNF-06: Trazabilidad de prompts IA
- Todos los prompts utilizados están documentados en PROMPTS.md
- Proveedor/modelo configurables por variables de entorno
"""

from __future__ import annotations
import time 
import asyncio
import json
import logging
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuración IA
# ---------------------------------------------------------------------------
# Asegura carga de .env también cuando este módulo se importa antes que main.py
load_dotenv()

# IA_PROVIDER: "gemini" | "groq" | "openai" (si está vacío se autodetecta)
IA_PROVIDER = (os.getenv("IA_PROVIDER") or "").strip().lower()

# Google AI Studio / Gemini Developer API (Generative Language API)
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Groq (OpenAI-compatible)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# OpenAI (legacy / opcional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _effective_provider() -> str:
    if IA_PROVIDER in ("gemini", "groq", "openai"):
        return IA_PROVIDER
    if GEMINI_API_KEY:
        return "gemini"
    if GROQ_API_KEY:
        return "groq"
    if OPENAI_API_KEY:
        return "openai"
    return "none"




def _gemini_generate_text(*, prompt: str, temperature: float, max_output_tokens: int) -> Optional[str]:
    if not GEMINI_API_KEY:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_output_tokens},
    }

    # IMPLEMENTACIÓN DE REINTENTO TÉCNICO (Máximo 3 intentos para errores 503/429)
    for intento in range(3):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
                # Si llegamos aquí, la respuesta fue exitosa
                candidates = data.get("candidates") or []
                content = candidates[0].get("content") if candidates else None
                parts = (content or {}).get("parts") or []
                return (parts[0].get("text") or "").strip() or None

        except urllib.error.HTTPError as e:
            # Si es 503 (Saturación) o 429 (Límite de cuota), esperamos y reintentamos
            if e.code in (503, 429):
                espera = (intento + 1) * 2  # Espera 2s, luego 4s...
                logger.warning(f"Gemini saturado (Error {e.code}). Reintentando en {espera}s...")
                time.sleep(espera)
                continue 
            
            logger.error("Error HTTP no recuperable %s", e.code)
            break # Errores como 400 o 404 no se arreglan reintentando
            
        except Exception as e:
            logger.error("Error de conexión IA: %s", str(e))
            break
            
    return None


def _openai_compatible_generate_text(
    *,
    api_key: Optional[str],
    base_url: str,
    model: str,
    provider_name: str,
    system: str,
    user: str,
    temperature: float,
    max_tokens: int,
) -> Optional[str]:
    if not api_key:
        return None
    try:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        req = urllib.request.Request(
            f"{base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            choices = data.get("choices") or []
            message = choices[0].get("message") if choices else None
            content = (message or {}).get("content")
            if isinstance(content, str):
                return content.strip() or None
            return None
    except Exception as e:
        logger.error("Error llamando a %s: %s", provider_name, str(e))
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
        logger.warning("IA no configurada (GOOGLE_API_KEY/GEMINI_API_KEY, GROQ_API_KEY u OPENAI_API_KEY).")
        return []

    base = [k.strip() for k in (keywords or []) if isinstance(k, str) and k.strip()]
    if not base:
        return []

    keywords_str = ", ".join(base)
    prompt = f"""
Eres un asistente especializado en generación de palabras clave relacionadas para motores de búsqueda de noticias.

Dadas estas palabras clave: {keywords_str}

Genera entre 4 y 5 sinónimos o palabras relacionadas cuando sea posible.
Si el término tiene pocas variantes reales, devuelve menos (1-3), pero prioriza 4-5 siempre que existan opciones válidas.
Las palabras deben ser:
- En español
- Relevantes al tema
- Que amplíen la cobertura sin ser demasiado genéricas
- Separadas por comas

Responde SOLO con las palabras, sin explicación adicional.
Ejemplo de respuesta: "economía digital, transformación digital, negocio electrónico"
""".strip()

    def _call_model(user_prompt: str) -> str:
        if provider == "gemini":
            return _gemini_generate_text(prompt=user_prompt, temperature=0.7, max_output_tokens=180) or ""
        if provider == "groq":
            return (
                _openai_compatible_generate_text(
                    api_key=GROQ_API_KEY,
                    base_url=GROQ_BASE_URL,
                    model=GROQ_MODEL,
                    provider_name="Groq",
                    system="Eres un asistente experto en generación de palabras clave para búsqueda de noticias.",
                    user=user_prompt,
                    temperature=0.7,
                    max_tokens=180,
                )
                or ""
            )
        return (
            _openai_compatible_generate_text(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_BASE_URL,
                model=OPENAI_MODEL,
                provider_name="OpenAI",
                system="Eres un asistente experto en generación de palabras clave para búsqueda de noticias.",
                user=user_prompt,
                temperature=0.7,
                max_tokens=180,
            )
            or ""
        )

    text = _call_model(prompt)
    synonyms = [s.strip() for s in text.split(",") if s.strip()]

    # Reintento dirigido: si salen pocas opciones pero el cliente admite >=4,
    # intentamos forzar mayor cobertura sin perder relevancia.
    target_min = min(4, max_synonyms)
    if len(synonyms) < target_min and max_synonyms >= 4:
        retry_prompt = (
            prompt
            + "\n\nNecesito al menos 4 opciones si existen. "
            "Si no hay 4 sinónimos estrictos, incluye términos relacionados de alta relevancia."
        )
        retry_text = _call_model(retry_prompt)
        retry_synonyms = [s.strip() for s in retry_text.split(",") if s.strip()]
        if len(retry_synonyms) > len(synonyms):
            synonyms = retry_synonyms

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
    elif provider == "groq":
        category = (
            _openai_compatible_generate_text(
                api_key=GROQ_API_KEY,
                base_url=GROQ_BASE_URL,
                model=GROQ_MODEL,
                provider_name="Groq",
                system="Eres un clasificador experto de noticias en categorías IPTC nivel 1.",
                user=prompt,
                temperature=0.3,
                max_tokens=50,
            )
            or "General"
        )
    else:
        category = (
            _openai_compatible_generate_text(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_BASE_URL,
                model=OPENAI_MODEL,
                provider_name="OpenAI",
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


async def generate_wordcloud_terms(*, texts: List[str], lang: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Genera una nube de terminos [{term, count}] a partir de textos (titulos/descripciones).

    PROMPT_ID: IA-003-WORDCLOUD
    """
    provider = _effective_provider()
    if provider == "none":
        return []

    # Recortamos entrada para evitar prompts enormes
    limit = max(5, min(int(limit), 50))
    joined = "\n\n---\n\n".join(texts[:200])
    joined = joined[:12000]

    language_name = "espanol" if (lang or "").lower().startswith("es") else "ingles"

    prompt = f"""
Vas a construir una nube de palabras para un dashboard de noticias.

Entrada: una lista de titulos y descripciones de noticias.
Objetivo: extraer las {limit} palabras o frases clave mas representativas.

Reglas:
- Idioma de salida: {language_name}
- Usa MAYUSCULAS en term
- Prioriza frases clave (1 a 3 palabras) frente a palabras sueltas
- No incluyas stopwords ni conectores (ej: "de", "la", "and")
- No incluyas nombres de secciones tipo "Opinion" si no aportan tema
- Devuelve JSON estricto: una lista de objetos con campos "term" (string) y "count" (int 1..100)
- Ordena por count descendente
- No devuelvas texto extra fuera del JSON

Noticias:
{joined}
""".strip()

    if provider == "gemini":
        raw = _gemini_generate_text(prompt=prompt, temperature=0.3, max_output_tokens=800) or "[]"
    elif provider == "groq":
        raw = (
            _openai_compatible_generate_text(
                api_key=GROQ_API_KEY,
                base_url=GROQ_BASE_URL,
                model=GROQ_MODEL,
                provider_name="Groq",
                system="Eres un asistente que extrae keywords para visualizaciones tipo wordcloud.",
                user=prompt,
                temperature=0.3,
                max_tokens=800,
            )
            or "[]"
        )
    else:
        raw = (
            _openai_compatible_generate_text(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_BASE_URL,
                model=OPENAI_MODEL,
                provider_name="OpenAI",
                system="Eres un asistente que extrae keywords para visualizaciones tipo wordcloud.",
                user=prompt,
                temperature=0.3,
                max_tokens=800,
            )
            or "[]"
        )

    try:
        data = json.loads(raw)
    except Exception:
        logger.error("Wordcloud: respuesta no es JSON: %s", raw[:200])
        return []

    if not isinstance(data, list):
        return []

    out: List[Dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        term = item.get("term")
        count = item.get("count")
        if not isinstance(term, str) or not term.strip():
            continue
        if not isinstance(count, int):
            try:
                count = int(count)
            except Exception:
                continue
        count = max(1, min(count, 100))
        out.append({"term": term.strip().upper(), "count": count})

    # Dedup simple
    seen = set()
    dedup: List[Dict[str, Any]] = []
    for it in out:
        k = it["term"]
        if k in seen:
            continue
        seen.add(k)
        dedup.append(it)
        if len(dedup) >= limit:
            break

    return dedup


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
