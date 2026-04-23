# Arquitectura de Tests - NewsRadar

## 1. Estructura del Proyecto de Tests

```
backend/tests/
├── conftest.py          # Fixtures compartidas y configuración pytest
├── app/
│   └── main.py          # Mock de la aplicación para tests
├── fixtures/
│   ├── feed_falso.xml   # XML de RSS simulado
│   ├── users_valid.json # Usuarios válidos para seeds
│   └── users_invalid.json # Usuarios inválidos para validación
├── test_smoke.py        # Pruebas de despliegue (health check)
├── test_auth.py         # Autenticación y autorización
├── test_usuario.py      # Gestión de perfiles de usuario
├── test_permisos.py     # RBAC (Role-Based Access Control)
├── test_alertas.py      # Gestión de alertas
├── test_worker_rss.py   # Procesamiento de feeds RSS
├── test_logic.py        # Lógica de negocio específica
├── test_db_connection.py # Conectividad a bases de datos
└── test_setup.py        # Configuración inicial y seeds
```

## 2. Configuración Central (conftest.py)

El archivo `conftest.py` centraliza todas las fixtures compartidas:

### Fixtures de Usuarios
```python
@pytest.fixture
def fixture_user_lector():
    """Simula usuario con rol Lector"""
    return {"id": 1, "email": "lector@newsradar.es", "role": "Lector"}

@pytest.fixture
def fixture_user_gestor():
    """Simula usuario con rol Gestor"""
    return {"id": 2, "email": "gestor@newsradar.es", "role": "Gestor"}
```

### Fixtures de Base de Datos
```python
@pytest.fixture
def db_engine():
    """Conexión a base de datos para tests"""
    # Conexión aislada, no afecta BD producción

@pytest.fixture
def client():
    """TestClient de FastAPI"""
    from fastapi.testclient import TestClient
    from newsradar_api.app.main import app
    return TestClient(app)
```

### Fixtures de Datos
```python
@pytest.fixture
def load_valid_users():
    """Carga usuarios válidos desde JSON"""
    with open("fixtures/users_valid.json") as f:
        return json.load(f)

@pytest.fixture
def mock_rss_xml():
    """Proporciona XML simulado de RSS"""
    with open("fixtures/feed_falso.xml") as f:
        return f.read()
```

## 3. Archivos de Test

### test_smoke.py - Pruebas de Despliegue
**Propósito:** Verificar que la API está funcional y lista
**Alcance:** Tests de integración rápidos
**Responsabilidades:**
- Endpoint `/api/v1/health` devuelve 200 OK
- Respuesta contiene `{"status": "ok", "timestamp": "..."}`

### test_auth.py - Autenticación
**Propósito:** Validar flujos de auth y tokens
**Alcance:** Integración de endpoints auth
**Tests:**
- Registro de nuevo usuario
- Email duplicado rechazado
- Login con credenciales válidas
- Login con credenciales inválidas
- Token Bearer válido/inválido

### test_usuario.py - Gestión de Usuarios
**Propósito:** CRUD de perfiles de usuario
**Alcance:** Endpoints `/api/v1/users`
**Tests:**
- Obtener perfil del usuario actual
- Listar todos los usuarios
- Actualizar datos de usuario
- Validación de campos obligatorios

### test_permisos.py - RBAC
**Propósito:** Control de acceso basado en roles
**Alcance:** Endpoints con restricción de permisos
**Tests:**
- Acceso denegado sin token (401)
- Gestor puede crear alerta (201)
- Lector bloqueado de crear alerta (403)
- Permisos correctos según roles asignados

### test_alertas.py - Gestión de Alertas
**Propósito:** CRUD de alertas y validaciones
**Alcance:** Endpoints `/api/v1/alerts`
**Tests:**
- Crear alerta con categoría válida
- Rechazar alerta con categoría IPTC inválida
- Obtener alertas del usuario
- Actualizar alerta existente
- Eliminar alerta
- Validación de descriptores

### test_worker_rss.py - Procesamiento RSS
**Propósito:** Validar parseo y procesamiento de feeds
**Alcance:** Worker asincrónico de monitorización
**Tests:**
- Parseo correcto de XML válido
- Rechazo de XML malformado
- Extracción de metadata (título, URL, etc.)
- Asociación a categoría IPTC
- Relación con alertas que coinciden

### test_logic.py - Lógica de Negocio
**Propósito:** Validar reglas de negocio
**Alcance:** Funciones de utilidad y validadores
**Tests:**
- Validación de expresiones cron
- Generación de sinónimos con IA
- Cálculo de métricas
- Clasificación IPTC

### test_db_connection.py - Conectividad
**Propósito:** Verificar conexiones a bases de datos
**Alcance:** Inicialización y health checks
**Tests:**
- Conexión a PostgreSQL exitosa
- Conexión a MongoDB exitosa
- Migraciones de Alembic aplicadas
- Esquema actualizado

### test_setup.py - Configuración Inicial
**Propósito:** Seeds y fixtures de datos
**Alcance:** Inicialización de BD para tests
**Tests:**
- Crear tablas en PostgreSQL
- Cargar datos iniciales
- Verificar seeding de usuarios por defecto
- Validar índices y constraints

## 4. Estrategia de Testing

### Decisiones de Diseño

#### 1. **TestClient en lugar de requests real**
```python
from fastapi.testclient import TestClient

client = TestClient(app)
response = client.post("/api/v1/auth/register", json=payload)
```
✅ No hace llamadas HTTP reales
✅ Más rápido que tests HTTP
✅ Aislado de configuración de puertos

#### 2. **Fixtures parametrizadas para casos múltiples**
```python
@pytest.mark.parametrize("email,expected", [
    ("valid@test.com", 201),
    ("invalid.com", 422),
])
def test_register(client, email, expected):
    assert client.post("/api/v1/auth/register", json={"email": email, ...}).status_code == expected
```

#### 3. **Mocks para servicios externos**
```python
with patch('requests.get') as mock_get:
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = feed_xml.encode()
    # Test sin acceder a internet
```

#### 4. **BD aislada para cada test**
- Tests usan BD de test (no la producción)
- Limpieza automática post-test
- Transacciones rollback en tests E2E

## 5. Flujo de Ejecución

### Comando Local
```bash
pytest                              # Todos los tests
pytest -v                           # Modo verbose
pytest --cov=newsradar_api          # Con cobertura
pytest backend/tests/test_auth.py   # Archivo específico
pytest -k "auth"                    # Por patrón de nombre
```

### Comando CI/CD (GitHub Actions)
```bash
pytest --cov=newsradar_api.app --cov-report=xml backend/tests/
```
- Genera reporte XML de cobertura
- Falla si cobertura < 70%
- Genera reportes en GitHub

## 6. Anatomía de un Test

```python
def test_auth_01_registro_exitoso(client, db_engine):
    # 1. ARRANGE: Preparar datos
    payload = {
        "username": "nuevo_tester",
        "email": "tester@newsradar.es",
        "password": "Password123!"
    }
    
    # 2. ACT: Ejecutar acción
    response = client.post("/api/v1/auth/register", json=payload)
    
    # 3. ASSERT: Verificar resultado
    assert response.status_code == 201
    assert response.json()["email"] == "tester@newsradar.es"
    assert "password" not in response.json()  # Nunca devolver contraseña
```

### Patrón AAA (Arrange-Act-Assert)
1. **Arrange:** Preparar datos y contexto
2. **Act:** Ejecutar la acción bajo prueba
3. **Assert:** Verificar que ocurrió lo esperado

## 7. Cobertura de Código

### Meta
- Mínimo 70% cobertura global
- 100% en lógica crítica (auth, RBAC)
- 90% en handlers de endpoints

### Medición
```bash
pytest --cov=newsradar_api --cov-report=html
# Genera reporte en htmlcov/index.html
```

### Exclusiones
- Puntos de entrada (if __name__ == "__main__")
- Código de logging
- Excepciones muy raras

## 8. Datos de Prueba

### fixtures/users_valid.json
```json
{
  "gestor_admin": {
    "email": "admin@test.com",
    "password": "Admin123!",
    "role": "Gestor"
  },
  "lector_basico": {
    "email": "lector@test.com",
    "password": "Lector123!",
    "role": "Lector"
  }
}
```

### fixtures/feed_falso.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Periódico Falso</title>
    <item>
      <title>La IA revoluciona la educación</title>
      <category>Tecnología</category>
      <link>https://example.com/noticia</link>
    </item>
  </channel>
</rss>
```

## 9. Integración Continua

### GitHub Actions
```yaml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres: ...
      mongodb: ...
    steps:
      - uses: actions/checkout@v3
      - run: pytest --cov=newsradar_api backend/tests/
```

### Criterios de Aceptación
✅ 100% de tests deben pasar
✅ Cobertura ≥ 70%
✅ Sin warnings de pytest
✅ Formatos de código válidos

## 10. Mejores Prácticas

| Práctica | Beneficio |
|----------|-----------|
| Fixtures reutilizables | Reduce duplicación |
| Tests independientes | Orden de ejecución flexible |
| Mocks para externos | Tests rápidos y confiables |
| Nombres descriptivos | Fallos claros al leer salida |
| Una asserción principal | Diagnosticar causa raíz fácil |
| Limpieza automática | No hay efectos secundarios |
| Tests de error | Robusto ante entrada inválida |

