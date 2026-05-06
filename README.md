# NewsRadar

API REST para monitorización de noticias basada en alertas RSS, construida con FastAPI y MongoDB.

## Requisitos

- Docker y Docker Compose instalados
- Puertos disponibles: 8000 (API), 27017 (MongoDB), 5173 (Frontend)

## Ejecución con Docker Compose

### Desarrollo (servicios principales)

```bash
docker-compose -f docker-compose.dev.yml up --build
```

Antes de levantar el stack, crea el archivo `.env` en la raíz del proyecto a partir de [`.env.example`](/home/xinbo/Documents/uc3m/curso_4/cuatrimestre_2/doss/NewsRadar/.env.example) y completa las variables de IA que vayas a usar. Para Groq:

```bash
IA_PROVIDER=groq
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-8b-instant
```

Esto inicia:
- **API** en `http://localhost:8000`
- **MongoDB** en `localhost:27017`
- **Frontend** en `http://localhost:5173`

### Producción

```bash
docker-compose up --build
```

Inicia todos los servicios definidos en `docker-compose.yml`.

### Tests

```bash
docker-compose -f docker-compose.test.yml up --build
```

## Servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| API | 8000 | Backend FastAPI |
| MongoDB | 27017 | Base de datos |
| Frontend | 5173 | Interfaz React |

## Documentación

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Autenticación

1. Usuario administrador inicial (creado automáticamente):
   - **email:** `admin@newsradar.com`
   - **password:** `admin123`

2. Obtener token en `POST /api/v1/auth/login`

3. Usar el token como `Bearer <token>` en el header `Authorization`.

## Estructura de endpoints

- `/api/v1/auth/*` — Autenticación (login, register, verify, reset-password)
- `/api/v1/users/*` — Gestión de usuarios
- `/api/v1/users/{user_id}/alerts/*` — Alertas y notificaciones
- `/api/v1/information-sources/*` — Fuentes de información
- `/api/v1/information-sources/{source_id}/rss-channels/*` — Canales RSS
- `/api/v1/categories/*` — Categorías (IPTC)
- `/api/v1/stats/*` — Estadísticas
- `/api/v1/health` — Endpoint de salud

## Entidades

- Usuarios, Roles, Alertas, Categorías, Notificaciones, Fuentes de información, Canales RSS, Stats
