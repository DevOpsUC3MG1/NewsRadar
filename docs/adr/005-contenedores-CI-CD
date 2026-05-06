# ADR-005: Estrategia de Contenerización y CI/CD

## Estado
Aceptado

## Fecha
2026-04-06

## Contexto
El proyecto requiere despliegues "One-Click" en entornos limpios y validación de calidad (>70% cobertura). Además, se necesita agilidad en desarrollo para que los cambios en el código se reflejen sin reconstruir imágenes constantemente.

## Decisión
Se adopta una Arquitectura de Composición de Docker Compose con tres archivos de configuración:

- **docker-compose.yml**: Configuración base de producción con 4 servicios
- **docker-compose.dev.yml**: Overrides para desarrollo con volúmenes
- **docker-compose.test.yml**: Configuración para tests (opcional)

## Servicios del Sistema

### 1. PostgreSQL 15-Alpine (db_postgres)
```yaml
image: postgres:15-alpine
container_name: newsradar_postgres
ports: 5432:5432
environment:
  - POSTGRES_USER: ${POSTGRES_USER}
  - POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  - POSTGRES_DB: ${POSTGRES_DB}
volumes:
  - postgres_data:/var/lib/postgresql/data
healthcheck: Comprueba que el servicio está listo
```

**Responsabilidades:**
- Almacenar usuarios, roles, alertas, fuentes RSS, notificaciones
- Gestionar integridad referencial
- Ejecutar migraciones Alembic

### 2. MongoDB 7.0 (db_mongodb)
```yaml
image: mongo:7.0
container_name: newsradar_mongodb
ports: 27017:27017
environment:
  - MONGO_INITDB_ROOT_USERNAME: ${MONGO_INITDB_ROOT_USERNAME}
  - MONGO_INITDB_ROOT_PASSWORD: ${MONGO_INITDB_ROOT_PASSWORD}
volumes:
  - mongodb_data:/data/db
```

**Responsabilidades:**
- Almacenar noticias indexadas (colección `news`)
- Búsqueda full-text por categoría IPTC
- Metadatos y sentimiento de noticias

### 3. API Backend (newsradar_api)
```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema para psycopg2 (driver PostgreSQL)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "newsradar_api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Stack:**
- Python 3.12 slim (minimalista, ~150MB)
- FastAPI con uvicorn
- SQLAlchemy 2.0 async + Alembic
- Motor para MongoDB async
- Pydantic para validación

**Endpoints expuestos:**
- API REST: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

**Depends on:**
- `db_postgres` (healthcheck: service_healthy)
- `db_mongodb` (service_started)

### 4. Frontend (newsradar_frontend)
```dockerfile
# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

CMD ["npm", "run", "dev", "--", "--host"]
```

**Stack:**
- Node.js 20 Alpine
- React.js 18
- Vite (bundler rápido)
- Componentes reutilizables
- i18n (ES/EN)

**Expuesto en:**
- `http://localhost:5173`

**Depends on:**
- `api` (se comunica vía http://api:8000)

## Arquitectura de Red

```
Internet
    ↓
[Host Machine]
    ↓
Docker Bridge Network (newsradar_network)
    ├── db_postgres (puerto 5432 interno)
    ├── db_mongodb (puerto 27017 interno)
    ├── newsradar_api (puerto 8000 → localhost:8000)
    └── newsradar_frontend (puerto 5173 → localhost:5173)
```

**Características:**
- Los servicios se comunican por nombre DNS (ej: `db_postgres` en lugar de `localhost`)
- Solo los puertos especificados en `ports:` están expuestos al host
- Variables de entorno inyectadas desde `.env`

## Volúmenes Persistentes

| Volumen | Servicio | Propósito |
|---------|----------|-----------|
| `postgres_data` | db_postgres | Almacenamiento de BD relacional |
| `mongodb_data` | db_mongodb | Almacenamiento de BD documental |
| `./backend:/app` (dev) | newsradar_api | Hot-reload en desarrollo |
| `./frontend:/app` (dev) | newsradar_frontend | Hot-reload en desarrollo |

## Configuración por Entorno

### Desarrollo (Día a día)
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

**Características:**
- Volúmenes bind-mount para hot-reload
- uvicorn en modo reload
- npm run dev con watch
- Acceso fácil a logs
- Cambios de código reflejados instantáneamente

### Testing
```bash
docker compose -f docker-compose.test.yml up
pytest backend/tests/ --cov=newsradar_api
```

**Características:**
- Base de datos de test limpia
- Contenedores efímeros
- Reporte de cobertura
- CI/CD automation

### Producción (Competición)
```bash
docker compose up --build
```

**Características:**
- Imágenes compiladas y optimizadas
- Sin volúmenes bind-mount
- Código estático copiado
- Réplica exacta de qué entregará el jurado

## Variables de Entorno (.env)

```bash
# PostgreSQL
POSTGRES_USER=newsradar_user
POSTGRES_PASSWORD=secure_password_123
POSTGRES_DB=newsradar_db
DATABASE_URL=postgresql+asyncpg://newsradar_user:secure_password_123@db_postgres:5432/newsradar_db

# MongoDB
MONGO_INITDB_ROOT_USERNAME=mongo_user
MONGO_INITDB_ROOT_PASSWORD=mongo_password_123
MONGODB_URL=mongodb://mongo_user:mongo_password_123@db_mongodb:27017

# Email (Gmail)
GMAIL_SENDER=tu_correo@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
FRONTEND_RESET_URL=http://localhost:5173/reset-password
FRONTEND_VERIFY_URL=http://localhost:5173/verify
```

## Healthcheck

Solo PostgreSQL incluye verificación de salud:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
  interval: 5s
  timeout: 5s
  retries: 5
```

**Propósito:** Garantizar que la API espera a PostgreSQL antes de iniciar

## Comandos Esenciales

| Comando | Propósito | Entorno |
|---------|-----------|---------|
| `docker compose -f docker-compose.yml -f docker-compose.dev.yml up` | Iniciar en desarrollo con hot-reload | Dev |
| `docker compose up --build` | Simular producción (competición) | Prod |
| `docker compose down -v` | Detener y limpiar volúmenes (reset total) | Todos |
| `docker compose logs -f api` | Ver logs del backend en tiempo real | Todos |
| `docker compose exec api bash` | Acceso shell al contenedor API | Dev |
| `docker compose ps` | Listar servicios en ejecución | Todos |

## Flujo de Despliegue

### 1. Desarrollo Local
```
git commit → docker compose -f docker-compose.yml -f docker-compose.dev.yml up
↓
Hot-reload → Cambios se ven instantáneamente
```

### 2. Pull Request
```
git push → GitHub Actions Pipeline
↓
docker compose -f docker-compose.test.yml up
↓
pytest --cov=newsradar_api --cov-report=xml
↓
Cobertura ≥ 70%? ✅ → Merge permitido | ❌ → Merge bloqueado
```

### 3. Competición (Día de Entrega)
```
git clone → docker compose up --build
↓
Esperamos 30 segundos (healthcheck)
↓
Accedemos a http://localhost:5173 y http://localhost:8000/docs
↓
Jurado prueba casos de uso
```

## Consecuencias

### Positivas
✅ **Consistencia:** Código que funciona en dev funciona idéntico en prod
✅ **Aislamiento:** Cada desarrollador tiene su propia instancia sin conflictos
✅ **One-Click:** Un único comando levanta todo el sistema
✅ **Reproducibilidad:** El jurado verá exactamente lo que probaste
✅ **Escalabilidad:** Fácil añadir más servicios (cache Redis, worker Celery, etc.)

### Negativas
⚠️ **Gestión .env:** Cada desarrollador debe configurar variables correctamente
⚠️ **Curva de aprendizaje:** Docker requiere comprensión de redes y volúmenes
⚠️ **Consumo de recursos:** 4 contenedores pueden usar 2-3GB de RAM
⚠️ **Debugging:** Logs distribuidos requieren `docker compose logs`

## Mejoras Futuras

1. **Redis:** Cache para tokens y sesiones
2. **Nginx:** Reverse proxy para producción real
3. **Prometheus + Grafana:** Monitorización de métricas
4. **Worker Celery:** Procesamiento asincrónico de RSS
5. **Backup automático:** Volumen de PostgreSQL snapshot diario