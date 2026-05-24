# Trazabilidad Requisitos-Código — NewsRadar

> Matriz que mapea cada requisito funcional (RF) y no funcional (RNF) a los
> archivos, funciones y tests que lo implementan.

---

## RF-01: Autenticación y Gestión de Usuarios

| ID | Requisito | Backend | Frontend | Tests |
|---|---|---|---|---|
| RF-01.1 | Registro con email y contraseña (≥6 caracteres) | `main.py:583-596` (`POST /register`) | `registro/registro.jsx:90-144` | `test_auth.py::test_auth_01_registro_exitoso` |
| RF-01.2 | Login con token Bearer | `main.py:448-464` (`POST /auth/token`) | `login/` → `authService.js` | `test_auth.py::test_login_exitoso` |
| RF-01.3 | Verificación de email vía Gmail | `main.py:92-126` (`send_verification_email`), `main.py:597-626` (`GET /verify`) | `verifyAcc/` | — |
| RF-01.4 | Recuperación de contraseña (token 1h) | `main.py:657-683` (`POST /forgot-password`), `main.py:686-713` (`POST /reset-password`), `main.py:129-164` (`send_reset_password_email`) | `forgotPwd/`, `changePwd/` | — |
| RF-01.5 | Reenvío de email de verificación | `main.py:629-654` (`POST /resend-verification`) | — | — |

---

## RF-02: Gestión de Roles y Permisos

| ID | Requisito | Backend | Frontend | Tests |
|---|---|---|---|---|
| RF-02.1 | Roles Gestor y Lector | `init_db.py:36-37` (creación), `models.py:7-10` (`RoleModel`) | `user_profile/user_profile.jsx:85-86` | `test_roles.py` |
| RF-02.2 | Control de acceso RBAC | `main.py:469-485` (`get_current_user`) — solo verifica token, **no implementa control por roles** | — | `test_permisos.py` (solo 401, no 403) |
| RF-02.3 | Asignación múltiple de roles | `UserModel.role_ids` (JSON) en `models.py:20` | — | — |

---

## RF-03: Gestión de Alertas

| ID | Requisito | Backend | Frontend | Tests |
|---|---|---|---|---|
| RF-03.1 | CRUD completo de alertas | `main.py:1162-1229` (CREATE), `main.py:1085-1115` (LIST), `main.py:1232-1259` (GET), `main.py:1260-1321` (UPDATE), `main.py:1322-1372` (DELETE) | `alerts/alerts.jsx` | `test_alertas.py` |
| RF-03.2 | Alertas con nombre, descriptores, categorías IPTC | `AlertModel` en `models.py:28-38`, `AlertCreate` en `main.py:242-243` | `alerts/alerts.jsx:162-165` (descriptores), `553-566` (categorías) | `test_alertas.py` |
| RF-03.3 | Expresión cron personalizable | `AlertModel.cron_expression` en `models.py:32`, validación `CronTrigger` en `main.py:1178-1181` | `alerts/alerts.jsx:504-524` (constructor cron 5 campos) | `test_alertas.py` |
| RF-03.4 | Solo Gestor puede crear alertas | `main.py:1162` — **no implementado**, cualquier usuario autenticado puede | — | — |

---

## RF-04: Categorización IPTC

| ID | Requisito | Backend | Frontend | Tests |
|---|---|---|---|---|
| RF-04.1 | Soporte categorías IPTC nivel 1 | `data/iptc_catalog.json` (17 cat.), `main.py:68-76` (carga), `seed.py:44-60` (persistencia) | `alerts/alerts.jsx:553-566` (selector radio) | `test_seed.py::test_load_iptc_catalog` |
| RF-04.2 | Validación categorías permitidas | `main.py:1198-1208` (validación contra catálogo) | — | `test_alertas.py::test_crear_alerta_categoria_invalida` |

---

## RF-05: Gestión de Fuentes RSS

| ID | Requisito | Backend | Frontend | Tests |
|---|---|---|---|---|
| RF-05.1 | CRUD fuentes de información | `main.py:1840-2071` (sources endpoints) | `fuentes/fuentes.jsx` | `test_sources.py` |
| RF-05.2 | CRUD canales RSS vinculados | `main.py:1928-1967` (channels bajo source) | `fuentes/fuentes.jsx:284-415` | `test_rss_channels.py` |
| RF-05.3 | Canal RSS con categoría IPTC | `RSSChannelModel.category_id` en `models.py:55` | — | `test_rss_channels.py` |

---

## RF-06: Sistema de Notificaciones

| ID | Requisito | Backend | Frontend | Tests |
|---|---|---|---|---|
| RF-06.1 | Registro de notificaciones con métricas | `main.py:1415-1465` (`POST /notifications`) | `notificaciones/notificaciones.jsx` | `test_notifications.py` |
| RF-06.2 | Métricas con nombre y valor | `main.py:167-169` (`MetricItem`) | — | — |
| RF-06.3 | Notificaciones con timestamp | `daemon.py:338` (`fired_at`), `main.py:1436` (`timestamp`) | — | — |

---

## RF-07: Estadísticas y Monitorización

| ID | Requisito | Backend | Frontend | Tests |
|---|---|---|---|---|
| RF-07.1 | Endpoint `/api/v1/health` | `main.py:557-559` | — | `test_smoke.py::test_system_up_and_running` |
| RF-07.2 | Estadísticas configurables | `analytics_service.py:197-254` (`build_dashboard`) | `dashboard/dashboard.jsx` | `test_analytics_service.py` |

---

## RF-08: Email de Notificación

| ID | Requisito | Backend | Frontend | Tests |
|---|---|---|---|---|
| RF-08.1 | Email de bienvenida | `main.py:92-126` | — | — |
| RF-08.2 | Email de verificación | `main.py:92-126` (reutilizado) | — | — |
| RF-08.3 | Email de recuperación | `main.py:129-164` | — | — |
| RF-08.4 | Gmail con contraseña de aplicación | `main.py:82-83` (`GMAIL_SENDER`, `GMAIL_APP_PASSWORD`) | — | — |

---

## RF-09: Organización de Usuarios

| ID | Requisito | Backend | Frontend | Tests |
|---|---|---|---|---|
| RF-09.1 | Campo organización obligatorio | `UserModel.organization` en `models.py:22`, `UserCreate` en `main.py:206-208` | `registro/registro.jsx:90-144` | — |
| RF-09.2 | Nombre y apellido del usuario | `UserModel.first_name`, `last_name` en `models.py:18-19` | `registro/registro.jsx:90-144` | — |

---

## RNF-01: Arquitectura y Stack Tecnológico

| ID | Requisito | Implementación |
|---|---|---|
| RNF-01.1 | API REST con FastAPI (Python 3.10+) | `main.py:34-38` (`FastAPI(title="NewsRadar API")`), `Dockerfile` base python:3.10-slim |
| RNF-01.2 | Documentación OpenAPI/Swagger en `/docs` | FastAPI auto-genera, accesible en `/docs` y `/redoc`. CI genera docs vía pdoc (`ci.yml:96-99`) |
| RNF-01.3 | PostgreSQL 15+ | `docker-compose.yml:7-19` (imagen postgres:15-alpine) |
| RNF-01.4 | MongoDB 7+ | `docker-compose.yml:24-34` (imagen mongo:7) |
| RNF-01.5 | ORM asíncrono SQLAlchemy 2.0 + Alembic | `database.py` (async engine), `migrations/` (Alembic), `models.py` (declarative) |

---

## RNF-02: Seguridad

| ID | Requisito | Implementación |
|---|---|---|
| RNF-02.1 | Token Bearer JWT | `main.py:439-482` (generación y validación) |
| RNF-02.2 | CORS para frontend localhost:5173 | `main.py:50-55` (`CORSMiddleware`) |
| RNF-02.3 | Validación email con Pydantic EmailStr | `main.py:207` (`EmailStr`) |
| RNF-02.4 | No devolver contraseñas en respuestas | `UserInDB` en `main.py:424` excluye password |
| RNF-02.5 | Tokens con expiración | `main.py:441` (`verification_tokens` en memoria sin TTL real) |
| RNF-02.6 | Password reset en memoria | `main.py:444` (`password_reset_tokens` dict) |

---

## RNF-03: Validación de Datos

| ID | Requisito | Implementación |
|---|---|---|
| RNF-03.1 | Validación automática con Pydantic | Todos los modelos heredan de `BaseModel` |
| RNF-03.2 | Códigos HTTP estándar | Uso de `HTTPException` con status codes 200, 201, 400, 401, 403, 404, 409, 422 |
| RNF-03.3 | Mensajes de error descriptivos | `detail` en todas las excepciones, ej: `detail="Máximo 20 alertas por usuario"` |

---

## RNF-04: Testing

| ID | Requisito | Implementación |
|---|---|---|
| RNF-04.1 | Pytest + pytest-cov | `pytest.ini`, `requirements.txt` |
| RNF-04.2 | Cobertura mínima 70% | `ci.yml` con `--cov-fail-under=50` (configurado a 50) |
| RNF-04.3 | Unitarias, Integración, E2E | `backend/tests/` (24 archivos): keyword_service (unitarias), test_analytics_service (integración), test_smoke (E2E) |
| RNF-04.4 | TestClient de FastAPI | `conftest.py` usa `ASGITransport` con `AsyncClient` |

---

## RNF-05: Escalabilidad

| ID | Requisito | Implementación |
|---|---|---|
| RNF-05.1 | Concurrencia async/await | Todo el backend usa `async def`, SQLAlchemy `AsyncSession`, Motor `AsyncIOMotorClient` |
| RNF-05.2 | APScheduler para RSS asíncrono | `daemon.py:442-458` usa `AsyncIOScheduler` con `CronTrigger` |

---

## RNF-06: Contenerización

| ID | Requisito | Implementación |
|---|---|---|
| RNF-06.1 | Docker Compose 4 servicios | `docker-compose.yml`: postgres, mongo, api, frontend |
| RNF-06.2 | Healthcheck en PostgreSQL | `docker-compose.yml:14-18` (`pg_isready`) |
| RNF-06.3 | Variables de entorno .env | `.env`, `.env.example`, `docker-compose.yml` usa `${VAR}` |

---

## RNF-07: Frontend

| ID | Requisito | Implementación |
|---|---|---|
| RNF-07.1 | React 18 + Vite | `frontend/package.json` (react 18, vite) |
| RNF-07.2 | Componentes reutilizables | `frontend/src/components/`: Badge, Button, Card, Input, Modal, Table |
| RNF-07.3 | Internacionalización ES/EN | `frontend/src/i18n.js`, `public/locales/{en,es}/translation.json` |
| RNF-07.4 | Headers diferenciados | `components/Header/Header.jsx` (autenticado), `components/HeaderNoUser/HeaderNoUser.jsx` (login) |
| RNF-07.5 | Sidebar de navegación | `components/Sidebar/Sidebar.jsx` con 6 enlaces + logout |

---

## RNF-08: DevOps

| ID | Requisito | Implementación |
|---|---|---|
| RNF-08.1 | CI/CD con GitHub Actions | `.github/workflows/`: `ci.yml`, `cd.yml`, `python_tests.yml`, `quality.yml`, `docker.yml` |
| RNF-08.2 | Scripts de automatización | `scripts/`: `build.sh`, `test.sh`, `deploy.sh`, `rollback.sh`, `seed.sh` |

---

## RNF-09: Documentación API

| ID | Requisito | Implementación |
|---|---|---|
| RNF-09.1 | Versión `/api/v1` | `main.py:48` (`API_PREFIX = "/api/v1"`) |
| RNF-09.2 | Tags de agrupación | `main.py` — tags en cada router: auth, users, alerts, categories, sources, channels, notifications, stats, system |

---

> **Última actualización:** 2026-05-24
> **Total requisitos:** 40 | **Implementados:** 34 | **Parciales:** 4 | **No implementados:** 2
