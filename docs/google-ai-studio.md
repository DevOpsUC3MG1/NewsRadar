# Sinonimos manuales y wordcloud determinista

La integración con Gemini, Groq y OpenAI se ha retirado del backend.

Estado actual:

- `POST /api/v1/alerts/suggest-synonyms` usa un diccionario manual
- la expansión de keywords del worker reutiliza MongoDB y, si falta, tira del diccionario manual
- la clasificación IPTC funciona con reglas locales
- la nube de palabras se genera por frecuencia de términos

## Configuración

Variable opcional:

```bash
MANUAL_SYNONYMS_FILE=./data/manual_synonyms.json
```

Si no se define, el backend usa `data/manual_synonyms.json` en la raíz del repo.

## Diccionario manual

Formato:

```json
{
  "inteligencia artificial": [
    "IA",
    "aprendizaje automatico",
    "machine learning"
  ]
}
```

Notas:

- la clave se normaliza para búsquedas sin acentos ni mayúsculas
- los valores se deduplican
- el endpoint devuelve como máximo `max_synonyms`

## Cache en MongoDB

Colección:

- `keyword_dictionary`

Esquema aproximado:

```json
{
  "keyword": "inteligencia artificial",
  "synonyms": ["IA", "aprendizaje automatico"],
  "provider": "manual",
  "updated_at": "2026-05-07T12:34:56Z"
}
```

## Verificación rápida

```bash
curl -s -X POST http://localhost:8000/api/v1/alerts/suggest-synonyms \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"keywords":["inteligencia artificial"],"max_synonyms":5}'
```
