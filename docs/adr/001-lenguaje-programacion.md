## #ADR-001: Elección de Python como Lenguaje Principal
**Estado:** Aceptado

**Contexto:** El backend de NEWSRADAR requiere un procesamiento de texto avanzado (NLP para la generación y expansión de descriptores de alertas), gestión de tareas asíncronas cronometradas y la orquestación de llamadas a servicios de IA generativa. Se necesita un lenguaje que soporte estas características de forma madura y se integre bien con el entorno tecnológico definido.

**Decisión:** Se utilizará **Python 3.11+** como lenguaje principal del backend.

**Consecuencias:**
* **Positivas:** Python cuenta con el ecosistema de librerías más maduro para integración con IA, procesamiento de texto (`NLTK`, `spaCy`) y clientes robustos para motores de búsqueda como Elasticsearch. Permite iteraciones de desarrollo muy rápidas.
* **Negativas:** El rendimiento en concurrencia pura es menor que el de lenguajes compilados, lo que obligará a realizar un diseño asíncrono cuidadoso para no bloquear el hilo principal.
* **Ejemplo Práctico:** Al usar Python, la expansión de descriptores con IA (RF-02) se puede implementar fácilmente consumiendo la API de un LLM mediante librerías oficiales (como `openai` o `langchain`) en apenas unas pocas líneas de código.
