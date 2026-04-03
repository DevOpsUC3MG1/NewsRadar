# ADR-001: Stack Tecnológico

## Estado
Aceptado

## Fecha
2026-03-07

## Contexto
El equipo necesita seleccionar el stack tecnológico completo para desarrollar
NewsRadar, un sistema de monitorización de noticias RSS con panel de mando,
gestión de alertas y clasificación IPTC automática.

El enunciado establece los siguientes requisitos arquitecturales obligatorios:
- Un sistema gestor de datos para las entidades del sistema
- Un sistema gestor de datos para la información capturada
- Una capa de lógica de negocio
- Una capa de visualización
- Un API REST documentada con OpenAPI

El enunciado recomienda explícitamente: Elasticsearch/MongoDB/SQLite para datos,
Apache Superset/Kibana o React/Angular para visualización, y Docker para
contenerización. Además exige uso intensivo de IA generativa.

Las opciones evaluadas fueron:

**Backend:**
- FastAPI (Python) vs Django REST vs Spring Boot (Java) vs Express (Node.js)

**Frontend:**
- React.js vs Angular.js vs Vue.js

**Base de datos relacional:**
- PostgreSQL vs SQLite vs MySQL

**Base de datos documental:**
- MongoDB vs Elasticsearch

**Contenerización:**
- Docker + Docker Compose vs despliegue manual

## Decisión

Se adopta el siguiente stack:

| Capa | Tecnología | Versión mínima |
|---|---|---|
| API REST | FastAPI (Python) | 0.110+ |
| ORM | SQLAlchemy 2.0 async + Alembic | 2.0+ |
| BD relacional | PostgreSQL | 15+ |
| BD documental | MongoDB | 7+ |
| Cliente MongoDB async | Motor | 3.3+ |
| Scheduler | APScheduler (AsyncIOScheduler) | 3.10+ |
| IA Generativa | OpenAI API (GPT-4o-mini) | - |
| Frontend | React.js 18 + Vite | 18+ |
| Gráficas | Recharts + react-wordcloud | - |
| Internacionalización | react-i18next | - |
| Contenerización | Docker + Docker Compose 2 | - |
| CI/CD | GitHub Actions | - |
| Calidad de código | SonarQube / SonarCloud | - |

**FastAPI** se elige sobre las alternativas porque:
- El enunciado proporciona directamente una aplicación FastAPI de referencia
  en el Anexo I, por lo que la compatibilidad está garantizada.
- Genera documentación Swagger/OpenAPI automáticamente desde los modelos
  Pydantic, cumpliendo el requisito de API documentada sin trabajo extra.
- Soporte nativo async/await, necesario para el worker de monitorización RSS
  y las llamadas concurrentes a la IA.
- Menor boilerplate que Django REST para una API pura sin servidor de plantillas.

**React.js** se elige sobre Angular y Vue porque:
- El equipo tiene mayor experiencia previa con React.
- La componentización facilita la implementación de feature flags (mostrar/ocultar
  secciones según /api/v1/config) necesaria para la competición.
- Ecosistema maduro: react-wordcloud para nubes de palabras, Recharts para
  estadísticas, react-i18next para el requisito bilingüe ES/EN.

**PostgreSQL** se elige sobre SQLite porque:
- SQLite no soporta concurrencia real, lo que es un problema con el scheduler
  escribiendo noticias mientras el frontend lee estadísticas.
- PostgreSQL es más representativo de un entorno de producción real.
- Soporte nativo de tipos JSON/JSONB para metadatos variables.

**MongoDB** se elige sobre Elasticsearch para las noticias capturadas porque:
- El volumen estimado es bajo (solo se almacenan noticias con match en alertas,
  no todos los ítems RSS), lo que no justifica la complejidad operacional de ES.
- MongoDB cubre búsqueda full-text e índices de texto suficientes para este caso.
- El aggregation pipeline cubre el caso de nubes de palabras por categoría IPTC.
- Consume significativamente menos recursos (~300MB vs ~1.5GB RAM en Docker).
- Cumple el requisito del enunciado de dos gestores de datos diferenciados.
- Ver análisis detallado en ADR-004.

## Consecuencias

**Positivas:**
- Stack coherente y bien integrado: FastAPI + SQLAlchemy + Alembic es una
  combinación estándar con amplia documentación.
- Un único comando (docker compose up) levanta todos los servicios.
- La generación automática de Swagger facilita la verificación funcional del
  Anexo I.
- El uso de Python en backend permite integrar fácilmente las librerías de
  IA (openai, feedparser, motor).

**Negativas / riesgos:**
- El equipo debe gestionar dos bases de datos en producción y en rollback.
- FastAPI async requiere atención a no mezclar código síncrono y asíncrono,
  especialmente en los workers de APScheduler.
- El consumo de RAM del stack completo en Docker (PG + MongoDB + API + Frontend)
  requiere una máquina con al menos 4GB disponibles.

## Referencias
- Requisitos relacionados: RF-01 al RF-15, RNF-01, RNF-02, RNF-05
- Enunciado sección 4: Entorno tecnológico
- Enunciado Anexo I: API de servicios REST
- Ver también: ADR-002 (autenticación), ADR-004 (MongoDB vs Elasticsearch)
