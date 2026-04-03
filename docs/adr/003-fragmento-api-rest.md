## #ADR-003: Framework para la API REST Backend
**Estado:** Aceptado

**Contexto:** El sistema debe ofrecer una API REST estrictamente documentada bajo el estándar OpenAPI y manejar alta concurrencia de entrada/salida para cumplir con los tiempos de respuesta exigidos (< 500ms en el percentil 95).

**Decisión:** Se adopta **FastAPI**.

**Consecuencias:**
* **Positivas:** FastAPI genera la especificación OpenAPI (Swagger) de forma automática a partir del código. Al estar construido sobre Starlette, ofrece soporte nativo para operaciones asíncronas (`async/await`), vital para no bloquear la API durante las peticiones a la IA o las descargas de RSS.
* **Negativas:** Obliga al equipo de desarrollo a utilizar librerías compatibles con asincronía (por ejemplo, el driver asíncrono de SQLAlchemy para PostgreSQL), lo cual tiene una curva de aprendizaje si solo se domina la programación síncrona.
