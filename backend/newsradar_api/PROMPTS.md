# Trazabilidad de Prompts IA - NewsRadar

Requisito RNF-06: Mantener registro documentado de todos los prompts IA utilizados en el sistema.

## IA-001: Generación de Sinónimos

**Ubicación**: `app/services/ia_service.py:generate_synonyms()`  
**Modelo**: Gemini (`GEMINI_MODEL`, por defecto `gemini-1.5-flash`) o OpenAI (`OPENAI_MODEL`)  
**Endpoint**: POST `/api/v1/alerts/suggest-synonyms`

### Propósito
Generar de 3 a 10 sinónimos o palabras relacionadas para mejorar la búsqueda de noticias dentro de una alerta.

### Prompt
```
Eres un asistente especializado en generación de palabras clave relacionadas para motores de búsqueda de noticias.

Dadas estas palabras clave: {keywords}

Genera entre 3 y 10 sinónimos o palabras relacionadas que podrían mejorar la búsqueda y captura de noticias relevantes.
Las palabras deben ser:
- En español
- Relevantes al tema
- Que amplíen la cobertura sin ser demasiado genéricas
- Separadas por comas

Responde SOLO con las palabras, sin explicación adicional.
Ejemplo de respuesta: "economía digital, transformación digital, negocio electrónico"
```

### Parámetros
- `temperature`: 0.7 (balance entre creatividad y consistencia)
- `max_tokens`: 150

### Ejemplo de uso
```json
POST /api/v1/alerts/suggest-synonyms
{
  "keywords": ["inteligencia artificial", "machine learning"],
  "max_synonyms": 5
}

Response:
{
  "keywords": ["inteligencia artificial", "machine learning"],
  "suggested_synonyms": [
    "deep learning",
    "redes neuronales",
    "algoritmos de aprendizaje",
    "IA generativa",
    "modelos predictivos"
  ]
}
```

### RF-02 (Sugerencias automáticas de sinónimos)
- Se ejecuta cuando el usuario crea una alerta
- El usuario puede aceptar o rechazar las sugerencias
- Lo aceptado se guarda como parte de los descriptores de la alerta

---

## IA-002: Clasificación Automática IPTC

**Ubicación**: `app/services/ia_service.py:classify_iptc_level1()`  
**Modelo**: Gemini (`GEMINI_MODEL`, por defecto `gemini-1.5-flash`) o OpenAI (`OPENAI_MODEL`)  
**Ejecución**: Automática en background durante ingestión RSS

### Propósito
Clasificar automáticamente cada noticia detectada en categorías IPTC de primer nivel.

### Prompt
```
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
{text_first_500_chars}

Responde SOLO con el nombre de la categoría, sin explicación.
```

### Parámetros
- `temperature`: 0.3 (baja variabilidad, clasificación consistente)
- `max_tokens`: 50

### Ejemplo de uso
Input:
```
title: "La IA revoluciona el sector bancario en 2024"
description: "Los bancos implementan soluciones de inteligencia artificial..."
```

Output: `Technology`

### RF-05 (Clasificación de información)
- Se ejecuta automáticamente para cada artículo del RSS
- La categoría se hereda o asigna según parámetros de la alerta
- Se almacena en MongoDB junto a la noticia

---

## Versión y Cambios

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0     | 20/04/2026 | Versión inicial con 2 prompts |

## Variables de Entorno Requeridas

```bash
GOOGLE_API_KEY=AIza...         # Tu API key de Google AI Studio (recomendado)
GEMINI_MODEL=gemini-1.5-flash  # Modelo a usar (por defecto)
IA_PROVIDER=gemini             # Opcional (autodetecta si hay GOOGLE_API_KEY)

# Groq (OpenAI-compatible):
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-8b-instant
# IA_PROVIDER=groq

# Legacy / opcional:
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
```

## Notas de Implementación

- Todos los prompts están optimizados para devolver respuestas estructuradas
- Los prompts usan idioma español para generar palabras clave relevantes
- La temperatura se ajusta según si se prioriza creatividad (0.7) o consistencia (0.3)
- Los prompts incluyen ejemplos ("few-shot") para mejorar la calidad de respuestas

## Auditoría y Monitorización

Cada llamada a IA se registra en logs con:
- Timestamp
- Prompt ID
- Entrada (primeras 100 chars)
- Salida
- Tiempo de ejecución
- Errores (si aplica)

Accederá en los logs de la aplicación:
```
INFO:newsradar_api.app.services.ia_service: Sinónimos generados para 'inteligencia artificial': [...]
INFO:newsradar_api.app.services.ia_service: Categoría IPTC asignada: Technology
```
