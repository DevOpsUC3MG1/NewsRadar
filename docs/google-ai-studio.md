# Google AI Studio (Gemini) en NewsRadar (Backend)

Este documento describe cómo configurar y usar **Google AI Studio (Gemini)** en el backend de NewsRadar para:

- generar sinónimos (diccionario de palabras clave)
- clasificar noticias en categorías IPTC (nivel 1)

## 1) Requisito de seguridad (API keys)

- **No pegues** la API key en el código ni la subas a Git.
- Configúrala por **variable de entorno**.
- Si una key se ha compartido por chat, correo o ha aparecido en logs, **revócala y genera una nueva**.

## 2) Variables de entorno

El backend soporta:

- Gemini (Google AI Studio) (recomendado)
- OpenAI (legacy/opcional)

Variables para Gemini:

```bash
GOOGLE_API_KEY=AIza...                 # requerido para Gemini
GEMINI_MODEL=gemini-1.5-flash          # opcional (por defecto gemini-1.5-flash)
# IA_PROVIDER=gemini                   # opcional (autodetecta Gemini si hay GOOGLE_API_KEY)
```

Notas:

- `GOOGLE_API_KEY` y `GEMINI_API_KEY` se aceptan. Prioriza `GOOGLE_API_KEY`.
- Si `IA_PROVIDER` no está definido, el backend **autodetecta**:
  - si hay `GOOGLE_API_KEY` => usa `gemini`
  - si no, pero hay `OPENAI_API_KEY` => usa `openai`
  - si no hay ninguna => IA deshabilitada (devuelve valores por defecto)

## 3) Dónde se configura (según cómo ejecutes)

### Opción A: Docker Compose (recomendado)

Pon las variables en el `.env` que estés usando con `docker compose` (normalmente el `.env` en la **raíz del repo**), por ejemplo:

```bash
GOOGLE_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-flash
```

Luego:

```bash
docker compose up --build
```

### Opción B: Backend local (sin Docker)

Pon las variables en `backend/newsradar_api/.env` (o en tu entorno del shell) y arranca FastAPI como lo tengáis configurado.

## 4) Dónde se usa en el código

El backend llama a Gemini desde:

- `backend/newsradar_api/app/services/ia_service.py`
  - `generate_synonyms(...)`: genera sinónimos a partir de keywords
  - `classify_iptc_level1(...)`: clasifica texto en una categoría IPTC nivel 1
  - `expand_keywords(...)`: amplía `descriptors` usando el diccionario en MongoDB y, si falta, llama IA y lo guarda

El worker RSS lo usa aquí:

- `backend/newsradar_api/app/services/rss_worker.py`
  - en `process_alert(...)` se llama a `expand_keywords(...)`
  - el matching de noticias se hace contra `descriptors + synonyms` (deduplicado)

## 5) Diccionario de palabras clave (MongoDB)

Colección en MongoDB:

- `keyword_dictionary`

Esquema aproximado del documento:

```json
{
  "keyword": "inteligencia artificial",
  "synonyms": ["IA generativa", "machine learning", "..."],
  "provider": "gemini|openai|api",
  "updated_at": "2026-04-30T12:34:56Z"
}
```

Política actual:

- Si existe un registro reciente, se reutiliza (cache).
- Si no existe o está “viejo”, `expand_keywords(...)` puede llamar IA, y luego guarda en `keyword_dictionary`.

Parámetros actuales (hardcode):

- `max_age_days=30`
- `max_synonyms_per_keyword=5`

## 6) Cómo probarlo

### 6.1) Probar el endpoint de sinónimos

1) Obtén token (login):

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@newsradar.com","password":"admin123"}'
```

Guarda el `access_token`.

2) Llama a sinónimos:

```bash
curl -s -X POST http://localhost:8000/api/v1/alerts/suggest-synonyms \
  -H "Authorization: Bearer TU_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"keywords":["inteligencia artificial"],"max_synonyms":5}'
```

Respuesta esperada (ejemplo):

```json
{
  "keywords": ["inteligencia artificial"],
  "suggested_synonyms": ["IA generativa", "aprendizaje automático", "..."]
}
```

Nota:

- Si envías **una sola keyword**, el backend intenta persistir el resultado en `keyword_dictionary` para reutilizarlo en el worker.

### 6.2) Probar que afecta a la detección en RSS

El worker RSS ahora hace matching usando keywords expandidas (descriptor + sinónimos).

Para validarlo de forma práctica:

1) Asegúrate de tener una alerta con `descriptors` (ej. `["inteligencia artificial"]`) y categorías con canales RSS asociados.
2) Ejecuta el ciclo del worker (según el scheduler/cron configurado en el backend).
3) Verifica en MongoDB que:
   - existe/actualiza `keyword_dictionary.keyword == "inteligencia artificial"`
   - se insertan noticias que coinciden con sinónimos aunque no contengan el descriptor exacto

## 7) Troubleshooting

### La IA devuelve vacío / "General"

Causas típicas:

- `GOOGLE_API_KEY` no está definida en el proceso/contenedor.
- Key inválida o revocada.
- El contenedor no ve el `.env` que tú estás editando.

Checklist:

- Confirma que el backend tiene `GOOGLE_API_KEY` en su entorno.
- Revisa logs del backend buscando errores `Gemini HTTPError ...`.

### Timeouts o errores de red

La llamada a Gemini es HTTP. Si estás en un entorno sin acceso a internet o con restricciones de red, fallará.

## 8) Trazabilidad de prompts (RNF-06)

Los prompts están documentados en:

- `backend/newsradar_api/PROMPTS.md`

