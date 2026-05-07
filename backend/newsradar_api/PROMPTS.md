# Trazabilidad funcional de sinonimos y clasificacion

La integración con proveedores de IA se ha retirado del backend.

Estado actual del módulo `app/services/keyword_service.py`:

- `generate_synonyms(...)`: usa un diccionario manual
- `classify_iptc_level1(...)`: clasifica por reglas locales
- `generate_wordcloud_terms(...)`: calcula la nube por frecuencia de términos

## Diccionario manual de sinonimos

Archivo por defecto:

```bash
data/manual_synonyms.json
```

Variable opcional:

```bash
MANUAL_SYNONYMS_FILE=./data/manual_synonyms.json
```

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

## Clasificacion IPTC

La categoría se obtiene por coincidencia de términos sobre reglas internas. Si no hay señales suficientes, se devuelve `General`.

## Observabilidad

Los logs relevantes del servicio incluyen:

```text
INFO:newsradar_api.app.services.keyword_service: Sinónimos manuales para inteligencia artificial: [...]
INFO:newsradar_api.app.services.keyword_service: No hay sinónimos manuales para blockchain en data/manual_synonyms.json
```
