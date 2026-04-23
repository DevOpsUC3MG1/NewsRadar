# Requisitos - NewsRadar

## Requisitos Funcionales (RF)

### RF-01: Autenticación y Gestión de Usuarios
- **RF-01.1**: Registro de nuevos usuarios con email y contraseña segura (mínimo 6 caracteres)
- **RF-01.2**: Login con credenciales y generación de token JWT Bearer
- **RF-01.3**: Verificación de email mediante enlace enviado por Gmail
- **RF-01.4**: Recuperación de contraseña mediante token con expiración de 1 hora
- **RF-01.5**: Reenvío de email de verificación

### RF-02: Gestión de Roles y Permisos
- **RF-02.1**: Dos roles: Gestor (crear alertas) y Lector (solo visualizar)
- **RF-02.2**: Control de acceso basado en roles (RBAC) con respuesta 403 Forbidden para accesos denegados
- **RF-02.3**: Asignación de múltiples roles a usuarios

### RF-03: Gestión de Alertas
- **RF-03.1**: CRUD completo de alertas (Create, Read, Update, Delete)
- **RF-03.2**: Alertas con nombre, descriptores (palabras clave) y categorías IPTC
- **RF-03.3**: Expresión cron personalizable para frecuencia de monitorización
- **RF-03.4**: Solo usuarios con rol Gestor pueden crear alertas

### RF-04: Categorización IPTC
- **RF-04.1**: Soporte para categorías de primer nivel IPTC
- **RF-04.2**: Validación de categorías permitidas en alertas y fuentes

### RF-05: Gestión de Fuentes RSS
- **RF-05.1**: CRUD de fuentes de información
- **RF-05.2**: CRUD de canales RSS vinculados a fuentes
- **RF-05.3**: Cada canal RSS está asociado a una categoría IPTC

### RF-06: Sistema de Notificaciones
- **RF-06.1**: Registro de notificaciones con métricas
- **RF-06.2**: Métricas incluyen nombre y valor numérico
- **RF-06.3**: Notificaciones almacenadas con timestamp

### RF-07: Estadísticas y Monitorización
- **RF-07.1**: Endpoint `/api/v1/health` que devuelve estado del sistema
- **RF-07.2**: Estadísticas con métricas configurables

### RF-08: Email de Notificación
- **RF-08.1**: Envío de emails de bienvenida tras registro
- **RF-08.2**: Envío de emails de verificación de cuenta
- **RF-08.3**: Envío de emails de recuperación de contraseña
- **RF-08.4**: Uso de Gmail con contraseña de aplicación (GMAIL_APP_PASSWORD)

### RF-09: Organización de Usuarios
- **RF-09.1**: Campo organización obligatorio en registro y perfil
- **RF-09.2**: Información adicional: nombre y apellido del usuario

---

## Requisitos No Funcionales (RNF)

### RNF-01: Arquitectura y Stack Tecnológico
- **RNF-01.1**: API REST con FastAPI (Python 3.10+)
- **RNF-01.2**: Documentación automática OpenAPI/Swagger en `/docs`
- **RNF-01.3**: Base de datos relacional: PostgreSQL 15+
- **RNF-01.4**: Base de datos documental: MongoDB 7+ (para noticias indexadas)
- **RNF-01.5**: ORM asíncrono con SQLAlchemy 2.0 + Alembic para migraciones

### RNF-02: Seguridad
- **RNF-02.1**: Token Bearer JWT para autenticación
- **RNF-02.2**: CORS habilitado para aplicación frontend en `localhost:5173`
- **RNF-02.3**: Validación de emails mediante Pydantic EmailStr
- **RNF-02.4**: Nunca devolver contraseñas en texto plano en respuestas API
- **RNF-02.5**: Tokens de verificación y recuperación con expiración
- **RNF-02.6**: Password reset tokens almacenados en memoria (producción: Redis)

### RNF-03: Validación de Datos
- **RNF-03.1**: Validación automática con modelos Pydantic
- **RNF-03.2**: Códigos de estado HTTP estándar: 200, 201, 400, 401, 403, 404, 409, 422
- **RNF-03.3**: Mensajes de error descriptivos en respuestas

### RNF-04: Testing
- **RNF-04.1**: Framework: Pytest con pytest-cov
- **RNF-04.2**: Cobertura mínima: 70%
- **RNF-04.3**: Tipos de pruebas: Unitarias, Integración, E2E (Smoke tests)
- **RNF-04.4**: TestClient de FastAPI para pruebas de endpoints

### RNF-05: Escalabilidad
- **RNF-05.1**: Soporte para concurrencia con async/await
- **RNF-05.2**: Preparado para scheduler APScheduler (procesamiento de RSS asincrónico)

### RNF-06: Contenerización
- **RNF-06.1**: Docker Compose con orquestación de 4 servicios:
  - PostgreSQL (BD relacional)
  - MongoDB (BD documental)
  - API FastAPI (Backend)
  - React Vite (Frontend)
- **RNF-06.2**: Healthcheck en PostgreSQL
- **RNF-06.3**: Variables de entorno gestionadas con `.env` y `.env.example`

### RNF-07: Frontend
- **RNF-07.1**: React.js 18 + Vite
- **RNF-07.2**: Componentes reutilizables: Badge, Button, Card, Input, Modal, Table
- **RNF-07.3**: Internacionalización (i18n) ES/EN
- **RNF-07.4**: Headers diferenciados: HeaderNoUser (login) y Header (autenticado)
- **RNF-07.5**: Sidebar de navegación

### RNF-08: DevOps
- **RNF-08.1**: CI/CD con GitHub Actions
- **RNF-08.2**: Scripts de automatización: build.sh, test.sh, deploy.sh, rollback.sh, seed.sh

### RNF-09: Documentación API
- **RNF-09.1**: Versión de API: `/api/v1`
- **RNF-09.2**: Tags de agrupación: auth, users, alerts, categories, sources, channels, notifications, stats, system
