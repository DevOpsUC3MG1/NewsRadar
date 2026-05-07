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
import re
import unicodedata
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
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
MANUAL_SYNONYMS_FILE = os.getenv(
    "MANUAL_SYNONYMS_FILE",
    str(Path(__file__).resolve().parents[4] / "data" / "manual_synonyms.json"),
)
_MANUAL_SYNONYMS_CACHE: Optional[Dict[str, List[str]]] = None


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

def _suggest_synonyms_with_source(keywords: List[str], max_synonyms: int = 5) -> tuple[List[str], str]:
    """
    PROMPT_ID: IA-001-SYNONYMS
    Descripción: Generación de sinónimos para descriptores de alertas
    """
    base = [k.strip() for k in (keywords or []) if isinstance(k, str) and k.strip()]
    if not base:
        return [], "none"

    max_synonyms = max(1, int(max_synonyms))
    manual_synonyms = _manual_synonyms_for_keywords(base, max_synonyms)
    if len(manual_synonyms) >= max_synonyms:
        logger.info("Sinónimos manuales para %s: %s", ", ".join(base), manual_synonyms)
        return manual_synonyms[:max_synonyms], "manual"

    provider = _effective_provider()
    if provider == "none":
        if manual_synonyms:
            logger.info("Sinónimos manuales para %s: %s", ", ".join(base), manual_synonyms)
        else:
            logger.warning(
                "Sin proveedor IA configurado y sin coincidencias en el diccionario manual (%s).",
                MANUAL_SYNONYMS_FILE,
            )
        return manual_synonyms[:max_synonyms], "manual" if manual_synonyms else "none"

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
    synonyms = manual_synonyms + [s.strip() for s in text.split(",") if s.strip()]

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
        retry_synonyms = manual_synonyms + [s.strip() for s in retry_text.split(",") if s.strip()]
        if len(retry_synonyms) > len(synonyms):
            synonyms = retry_synonyms

    clean: List[str] = []
    seen = set()
    base_normalized = {_normalize_keyword(item) for item in base}
    for synonym in synonyms:
        normalized = _normalize_keyword(synonym)
        if not normalized or normalized in base_normalized or normalized in seen:
            continue
        seen.add(normalized)
        clean.append(synonym.strip())

    source = provider if clean else ("manual" if manual_synonyms else provider)
    logger.info("Sinónimos generados para %s: %s", keywords_str, clean)
    return clean[:max_synonyms], source


def generate_synonyms(keywords: List[str], max_synonyms: int = 5) -> List[str]:
    synonyms, _ = _suggest_synonyms_with_source(keywords, max_synonyms)
    return synonyms


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
        logger.warning("IA no configurada para wordcloud; usando fallback determinista.")
        return _fallback_wordcloud_terms(texts=texts, lang=lang, limit=limit)

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
        return _fallback_wordcloud_terms(texts=texts, lang=lang, limit=limit)

    if not isinstance(data, list):
        return _fallback_wordcloud_terms(texts=texts, lang=lang, limit=limit)

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

    return dedup or _fallback_wordcloud_terms(texts=texts, lang=lang, limit=limit)


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
        if not cached:
            generated, source = await asyncio.to_thread(_suggest_synonyms_with_source, [kw], max_synonyms_per_keyword)
            cached = generated or []
            if cached:
                await upsert_synonyms(mongo_db, keyword=kw, synonyms=cached, provider=source or provider)

        for syn in cached[:max_synonyms_per_keyword]:
            low = syn.lower()
            if low in seen:
                continue
            seen.add(low)
            out.append(syn)

    return out
