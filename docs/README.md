# 📚 Documentación - NewsRadar

Bienvenido a la documentación del proyecto NewsRadar. Este directorio contiene toda la información necesaria para entender, desarrollar y desplegar el sistema.

---

## 📖 Guía de Documentos

### 🚀 Empezar Aquí

1. **[requirements.md](requirements.md)** - Requisitos funcionales y no funcionales
   - Qué necesita hacer el sistema
   - Características implementadas
   - Stack tecnológico completo

### 🏗️ Arquitectura

2. **[architecture/modeloDatos.md](architecture/modeloDatos.md)** - Modelo de datos
   - Esquema PostgreSQL (usuarios, alertas, notificaciones)
   - Esquema MongoDB (notificaciones indexadas)
   - Migraciones Alembic
   - Índices recomendados

3. **[frontend-architecture.md](frontend-architecture.md)** - Arquitectura Frontend
   - Estructura de directorios React
   - Componentes reutilizables
   - Internacionalización (i18n)
   - Servicios HTTP

4. **[API-endpoints.md](API-endpoints.md)** - Referencia de endpoints
   - Todos los endpoints REST disponibles
   - Ejemplos de request/response
   - Códigos de estado HTTP
   - Documentación interactiva (Swagger)

### ✅ Testing y QA

5. **[requirements.md](testing_requirement.md)** - Estrategia de QA
   - Framework: Pytest con 70% cobertura
   - Tipos de pruebas (unitarias, integración, E2E)
   - Integración Continua

6. **[test_cases_auth.md](test_cases_auth.md)** - Casos de prueba
   - Autenticación y autorización
   - RBAC (Role-Based Access Control)
   - Gestión de usuarios
   - Tabla de casos de prueba ejecutados

7. **[test-architecture.md](test-architecture.md)** - Arquitectura de tests
   - Estructura de carpeta tests/
   - Fixtures compartidas (conftest.py)
   - Patrón AAA (Arrange-Act-Assert)
   - Estrategia de mocks y fixtures

### 🐳 DevOps

8. **[adr/005-contenedores-CI-CD](adr/005-contenedores-CI-CD)** - Contenerización
   - Docker Compose con 4 servicios
   - Dockerfiles backend y frontend
   - Volúmenes y persistencia
   - Comandos esenciales

### 📋 Arquitectura de Decisiones (ADRs)

9. **[adr/ADR-001-stack-tecnologico.md](adr/ADR-001-stack-tecnologico.md)**
   - Stack tecnológico elegido
   - Justificación de tecnologías
   - Alternativas evaluadas

10. **[adr/002-bases-datos.md](adr/002-bases-datos.md)**
    - PostgreSQL vs SQLite
    - MongoDB vs Elasticsearch

11. **[adr/003-fragmento-api-rest.md](adr/003-fragmento-api-rest.md)**
    - Diseño de API REST
    - Versionado (/api/v1)

12. **[adr/004-motor-tareas](adr/004-motor-tareas)**
    - APScheduler para procesamiento RSS
    - Worker asincrónico

13. **[adr/006-configuracion-dinamica](adr/006-configuracion-dinamica)**
    - Feature flags
    - Configuración remota

### 📊 Otros Documentos

14. **[competition-playbook.md](competition-playbook.md)** - Guía de competición
    - Requisitos específicos de la competencia

---

## 🔗 Flujo de Lectura Recomendado

### Para Nuevos Desarrolladores
```
1. requirements.md (¿Qué hace el sistema?)
   ↓
2. architecture/modeloDatos.md (¿Cómo se guardan los datos?)
   ↓
3. API-endpoints.md (¿Cómo se comunica?)
   ↓
4. frontend-architecture.md (¿Cómo se ve?)
   ↓
5. adr/005-contenedores-CI-CD (¿Cómo se despliega?)
```

### Para QA Engineers
```
1. test_cases_auth.md (Casos de prueba)
   ↓
2. testing_requirement.md (Estrategia de QA)
   ↓
3. test-architecture.md (Cómo están estructurados los tests)
```

### Para DevOps / Infraestructura
```
1. adr/005-contenedores-CI-CD (Docker Compose)
   ↓
2. requirements.md (Stack tecnológico)
   ↓
3. architecture/modeloDatos.md (BD: PostgreSQL + MongoDB)
```

### Para Arquitectos
```
1. adr/ (todos los ADRs)
   ↓
2. architecture/ (diagramas y modelos)
   ↓
3. requirements.md (requisitos implementados)
```

---

## 🎯 Características Documentadas

### Módulo de Autenticación
- ✅ Registro con email/contraseña
- ✅ Verificación de email
- ✅ Login con JWT Bearer
- ✅ Recuperación de contraseña
- ✅ RBAC (Gestor vs Lector)

### Módulo de Alertas
- ✅ CRUD de alertas
- ✅ Validación de categorías IPTC
- ✅ Descriptores y palabras clave
- ✅ Expresión cron personalizable

### Módulo de Notificaciones
- ✅ Almacenamiento en MongoDB
- ✅ Métricas configurables
- ✅ Timestamp de generación

### Frontend
- ✅ React.js 18 + Vite
- ✅ Componentes reutilizables
- ✅ Internacionalización (ES/EN)
- ✅ Gráficas con Recharts
- ✅ Nubes de palabras

### DevOps
- ✅ Docker Compose multi-servicio
- ✅ PostgreSQL + MongoDB
- ✅ Hot-reload en desarrollo
- ✅ CI/CD listo

---

## 📝 Cómo Contribuir a la Documentación

1. **Encontraste un error en la documentación?**
   - Abre un issue describiendo el error
   - Cita línea y documento

2. **Quieres mejorar un documento?**
   - Edita el archivo en `docs/`
   - Usa Markdown con encabezados claros
   - Añade ejemplos de código

3. **Documentación de nueva funcionalidad?**
   - Crea `docs/feature-nombre.md`
   - Sigue el patrón de documentos existentes
   - Referencia desde este README

---

## 🔍 Búsqueda Rápida

### ¿Cómo hago para...?

| Pregunta | Respuesta |
|----------|-----------|
| Entender la estructura de datos | [architecture/modeloDatos.md](architecture/modeloDatos.md) |
| Ver todos los endpoints | [API-endpoints.md](API-endpoints.md) |
| Ejecutar tests | [test-architecture.md](test-architecture.md) |
| Desplegar con Docker | [adr/005-contenedores-CI-CD](adr/005-contenedores-CI-CD) |
| Internacionalizar una página | [frontend-architecture.md](frontend-architecture.md) |
| Crear un nuevo test | [test_cases_auth.md](test_cases_auth.md) |
| Cambiar contraseña | [test_cases_auth.md](test_cases_auth.md) → AUTH-20 |

---

## 📚 Referencias Externas

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Pytest Guide](https://docs.pytest.org/)
- [Docker Compose Docs](https://docs.docker.com/compose/)

---

## ✨ Últimas Actualizaciones

- **2026-04-23:** Actualización completa de documentación
  - Añadido `test-architecture.md`
  - Actualizado `modeloDatos.md` con esquema actual
  - Creado `API-endpoints.md` con todos los endpoints
  - Creado `frontend-architecture.md`
  - Actualizado `005-contenedores-CI-CD`

---

**¿Preguntas o sugerencias?** 📧 Contacta al equipo en el canal de Slack #documentation

