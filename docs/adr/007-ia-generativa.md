# ADR-006: Estrategia de Integración de IA Generativa y Gestión de Prompts

## Estado
Aceptado

## Fecha
2026-04-12

## Contexto
NewsRadar requiere capacidades cognitivas para dos funciones críticas:
1. **RF-02 (Sinónimos):** Generar de 3 a 10 descriptores relacionados con una alerta.
2. **RF-05 (Clasificación IPTC):** Categorizar noticias capturadas en categorías de primer nivel.

Se debe garantizar una respuesta rápida, un coste controlado y, sobre todo, una estructura de datos que el backend pueda procesar automáticamente (JSON) sin texto explicativo innecesario del modelo.

## Decisión
Se adopta el uso de **OpenAI API (GPT-4o-mini)** mediante la librería oficial de Python, bajo la siguiente estrategia:

1. **Structured Outputs (JSON Mode):** Se forzará al modelo a responder exclusivamente en formato JSON mediante *Pydantic Logit Bias* o el parámetro `response_format: { "type": "json_object" }`. Esto evita errores de parseo en el backend.
2. **System Prompts Inmutables:** Los prompts se almacenarán en archivos de configuración (no embebidos en el código) para permitir ajustes sin recompilar.
3. **Fallback / Estrategia de Error:** Si la IA no responde o el JSON es inválido, el sistema asignará la categoría "Unassigned" y dejará los sinónimos vacíos, permitiendo que el flujo del programa continúe (resiliencia).
4. **Caché de Resultados:** Para evitar costes redundantes, si dos usuarios crean alertas con el mismo término exacto, se reutilizarán los sinónimos generados previamente y almacenados en caché/BD.

## Consecuencias

**Positivas:**
- **Precisión:** GPT-4o-mini ofrece un equilibrio perfecto entre comprensión semántica y velocidad para tareas de clasificación.
- **Trazabilidad:** Al separar los prompts en archivos de texto, podemos incluirlos en la documentación de "Trazabilidad de IA" que exige el proyecto.
- **Coste:** El uso de un modelo "mini" permite procesar miles de noticias dentro del presupuesto gratuito o mínimo de la API.

**Negativas / Riesgos:**
- **Dependencia de Terceros:** Si la API de OpenAI cae, la clasificación automática se detiene (mitigado por el ADR-006 de Feature Flags para desactivar el módulo).
- **Alucinaciones:** Existe el riesgo de que la IA invente categorías IPTC inexistentes. Se mitigará mediante una validación post-procesado contra una lista blanca de categorías oficiales.

## Ejemplo de Prompt (System Message)
"Eres un experto en taxonomía IPTC. Tu tarea es recibir el título y resumen de una noticia y devolver únicamente un JSON con la categoría de primer nivel (ej: 'Economy', 'Sport', 'Politics'). No escribas explicaciones."
