# Estrategia de QA - NewsRadar

## 1. Herramientas
- **Framework:** Pytest
- **Cobertura:** pytest-cov (Objetivo: >70%)
- **Cliente HTTP:** httpx (para TestClient de FastAPI)
- **Fixtures:** conftest.py centralizado para gestión de datos de prueba
- **Integración Continua:** GitHub Actions ejecutan los tests en cada Push

## 2. Tipos de Pruebas

### Pruebas Unitarias (60% del esfuerzo)
- Validación de modelos Pydantic (UserCreate, AlertCreate, etc.)
- Validación de cambios de contraseña
- Validación de emails con EmailStr
- Lógica de negocio de roles y permisos

### Pruebas de Integración (30% del esfuerzo)
- Endpoints de FastAPI con TestClient
- Conexión con PostgreSQL (CRUD de usuarios, alertas, etc.)
- Conexión con MongoDB (si aplica)
- Autenticación JWT Bearer
- Gestión de tokens y verificación

### Pruebas E2E / Smoke (10% del esfuerzo)
- Verificación de salud del sistema: `/api/v1/health`
- Flujos completos: Registro → Verificación → Login → Crear Alerta
- Comportamiento del worker RSS (con mocks)

## 3. Suite de Pruebas Implementadas

| Archivo | Propósito | Casos de Prueba |
|---------|-----------|-----------------|
| **test_smoke.py** | Verificación de despliegue | `test_system_up_and_running` - ¿Responde la API? |
| **test_auth.py** | Autenticación y registro | Registro exitoso, email duplicado, login, credenciales inválidas |
| **test_usuario.py** | Gestión de perfiles | Datos correctos del perfil, email del usuario |
| **test_permisos.py** | RBAC (Role-Based Access Control) | Acceso sin token, bloqueo a Lectores, permisos de Gestores |
| **test_alertas.py** | Gestión de alertas | Crear alerta exitosa, validación de categorías IPTC |
| **test_worker_rss.py** | Procesamiento de feeds RSS | Parseo de XML con mocks, validación de noticias |
| **test_logic.py** | Lógica de negocio | (Específico del proyecto) |
| **test_db_connection.py** | Conectividad a BD | Verificación de conexión PostgreSQL y MongoDB |
| **test_setup.py** | Configuración inicial | Seeding de datos, creación de esquemas |

## 4. Configuración de Fixtures (conftest.py)

Se definen fixtures reutilizables para:
- **Usuarios de prueba:** `fixture_user_lector`, `fixture_user_gestor`
- **Alertas de prueba:** `fixture_alerta_base`
- **Cliente HTTP:** TestClient de FastAPI
- **Base de datos:** Conexión sincrónica para tests
- **XML de RSS:** `mock_rss_xml` para pruebas del worker

## 5. Verificaciones Críticas

Se ejecutan pruebas automáticas sobre:
- ✅ **Autenticación:** Registro con email único, login exitoso
- ✅ **Roles de usuario:** Lector vs Gestor con permisos diferenciados
- ✅ **Categorías IPTC:** Solo categorías válidas se aceptan en alertas
- ✅ **Validación de datos:** Emails válidos, contraseñas seguras (>6 caracteres)
- ✅ **Códigos HTTP:** 201 (created), 401 (unauthorized), 403 (forbidden), 409 (conflict)
- ✅ **Salud del sistema:** Endpoint `/health` siempre disponible

## 6. Gestión de Datos en Pruebas

- Se utilizan fixtures en conftest.py para no ensuciar la BD real
- Cada test de integración debe dejar la BD como la encontró (limpieza automática)
- Mocks para servicios externos (Gmail, RSS feeds)
- TestClient de FastAPI usa una conexión de test aislada

## 7. Cobertura de Código

- **Meta:** Mínimo 70%
- **Medición:** `pytest --cov=newsradar_api.app --cov-report=html`
- **Enfoque:** Funciones críticas (auth, RBAC, alerts, validators)

## 8. CI/CD Integration

- Tests ejecutados automáticamente en cada push a `develop` o `main`
- Gatekeeper: No merge sin tests pasados y cobertura ≥70%
- Reportes de cobertura disponibles en GitHub Actions