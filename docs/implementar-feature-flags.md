# Implementar Feature Flags

El proyecto tiene dos flags definidos en `.env` y `.env.example` que **no están implementados en el backend**:

```env
FEATURE_FLAG_WORDCLOUD=true
FEATURE_FLAG_BILINGUAL=true
```

Necesitamos añadir guard clauses para que desactivar la flag realmente desactive la funcionalidad.

---

## 1. FEATURE_FLAG_WORDCLOUD

**Objetivo**: al poner `FEATURE_FLAG_WORDCLOUD=false`, los endpoints de wordcloud deben devolver `503 Service Unavailable`.

### Archivo a modificar

`backend/newsradar_api/app/services/analytics_service.py`

### Cambio necesario

Añadir esta guard clause al inicio de `build_wordcloud()` (línea ~228):

```python
import os

async def build_wordcloud(...):
    if os.getenv("FEATURE_FLAG_WORDCLOUD", "true").lower() == "false":
        raise HTTPException(status_code=503, detail="Wordcloud feature disabled")
    # ... resto del código existente
```

### Dependencias a añadir

```python
from fastapi import HTTPException
```

(ya existe `HTTPException` en `main.py`, pero en `analytics_service.py` habrá que importarlo)

### Tests

Añadir en `backend/tests/test_analytics_service.py`:

```python
async def test_wordcloud_disabled_via_flag(async_client):
    import os
    os.environ["FEATURE_FLAG_WORDCLOUD"] = "false"
    response = await async_client.get("/api/v1/resumen/clouds/global")
    assert response.status_code == 503
    os.environ["FEATURE_FLAG_WORDCLOUD"] = "true"
```

> **Alternativa más limpia**: usar `monkeypatch` de pytest.

---

## 2. FEATURE_FLAG_BILINGUAL

**Objetivo**: al poner `FEATURE_FLAG_BILINGUAL=false`, ignorar el header `Accept-Language` y devolver siempre etiquetas/localización en inglés (o español — decidid).

### Archivo a modificar

`backend/newsradar_api/app/services/analytics_service.py`

### Cambio necesario

Modificar `_parse_lang()` (línea ~25) para que cuando la flag esté desactivada fuerce un idioma fijo:

```python
import os

def _parse_lang(accept_language):
    if os.getenv("FEATURE_FLAG_BILINGUAL", "true").lower() == "false":
        return "en"  # o "es", según decisión del equipo
    # ... resto del código existente
```

### Consecuencia

Al forzar `lang` desde `_parse_lang()`, todos los sitios que usan esa variable se ven afectados automáticamente:
- Etiquetas del dashboard (`dashboard_category_label`, `news_category_label`)
- Días de la semana (`dow_label`)
- Stopwords del wordcloud

No hace falta modificar nada más.

### Tests

Añadir en `backend/tests/test_misc_endpoints.py` o test nuevo:

```python
async def test_bilingual_disabled_via_flag(async_client):
    import os
    os.environ["FEATURE_FLAG_BILINGUAL"] = "false"
    response = await async_client.get(
        "/api/v1/dashboard",
        headers={"accept-language": "es"}
    )
    # Verificar que las etiquetas están en inglés
    data = response.json()
    # assert "Politics" in str(data) ...
    os.environ["FEATURE_FLAG_BILINGUAL"] = "true"
```

---

## 3. Recordatorio final

Después de implementar ambos flags, ejecutar:

```bash
ruff check .
flake8 . --exclude=backend/migrations --max-line-length=120

DATABASE_URL="postgresql+asyncpg://newsuser:newspassword@localhost:5432/newsradar_db" \
MONGODB_URL="mongodb://admin:adminpassword@localhost:27017" \
ENV=testing python -m pytest backend/tests/ -v --cov=backend/newsradar_api --cov-report=term
```
