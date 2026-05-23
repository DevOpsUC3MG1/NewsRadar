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

8. **[adr/005-contenedores-CI-CD.md](adr/005-contenedores-CI-CD.md)** - Contenerización
   - Docker Compose con 4 servicios
   - Dockerfiles backend y frontend
   - Volúmenes y persistencia
   - Comandos esenciales

### 📋 Arquitectura de Decisiones (ADRs)

9. **[adr/001-stack-tecnologico.md](adr/001-stack-tecnologico.md)**
   - Stack tecnológico elegido
   - Justificación de tecnologías
   - Alternativas evaluadas

10. **[adr/002-autenticacion.md](adr/002-autenticacion.md)**
    - Autenticación JWT
    - RBAC

11. **[adr/003-feature-flags.md](adr/003-feature-flags.md)**
    - Feature flags por variable de entorno
    - Desactivación remota

12. **[adr/004-motor-tareas.md](adr/004-motor-tareas.md)**
    - APScheduler para procesamiento RSS
    - Persistencia poliglota (PG + Mongo)

13. **[adr/006-i8n.md](adr/006-i8n.md)**
    - Internacionalización ES/EN
    - i18next en frontend

### 📊 Otros Documentos

14. **[competition-playbook.md](competition-playbook.md)** - Guía de competición
    - Procedimientos para añadir/desactivar funcionalidad
    - Rollback a versión previa

15. **[ROADMAP.md](../ROADMAP.md)** - Hoja de ruta del proyecto
    - Hitos completados y pendientes
    - Plan de trabajo hasta la competición

16. **[pyproject.toml](../pyproject.toml)** - Configuración consolidada
    - Dependencias del proyecto
    - Configuración de pytest, coverage, Ruff

### 🖼️ Diagramas de Arquitectura

17. **[architecture/container-diagram.puml](architecture/container-diagram.puml)** - Diagrama C4 de contenedores
    - Componentes del sistema y sus relaciones

18. **[architecture/container-diagram.puml](architecture/container-diagram.puml)** - Diagrama unificado de arquitectura
    - Componentes, puertos, healthchecks, variables de entorno, flujo de datos

### 📄 Generación de Documentación

19. **[scripts/docs.sh](../scripts/docs.sh)** - Script de generación automática
    - Genera documentación API con pdoc
    - Salida en `docs/api/index.html`

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
5. adr/005-contenedores-CI-CD.md (¿Cómo se despliega?)
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
1. adr/005-contenedores-CI-CD.md (Docker Compose)
   ↓
2. requirements.md (Stack tecnológico)
   ↓
3. architecture/modeloDatos.md (BD: PostgreSQL + MongoDB)
   ↓
4. architecture/container-diagram.puml (Diagrama unificado)
```

### Para Arquitectos
```
1. adr/ (todos los ADRs)
   ↓
2. architecture/ (diagramas, modelos, PUML)
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
| Desplegar con Docker | [adr/005-contenedores-CI-CD.md](adr/005-contenedores-CI-CD.md) |
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

- **2026-05-23:** Preparación competición
  - Añadidos diagramas C4 y despliegue (PlantUML)
  - Creado `scripts/docs.sh` (generación automática con pdoc)
  - Creado `ROADMAP.md` con hoja de ruta
  - Creado `pyproject.toml` con config consolidada (pytest, coverage, Ruff)
  - Configurado Ruff como linter
  - CD mejorado con push a GHCR
  - Normalizados ADRs a extensión `.md`

- **2026-04-23:** Actualización completa de documentación
  - Añadido `test-architecture.md`
  - Actualizado `modeloDatos.md` con esquema actual
  - Creado `API-endpoints.md` con todos los endpoints
  - Creado `frontend-architecture.md`
  - Actualizado `005-contenedores-CI-CD.md`

---

**¿Preguntas o sugerencias?** 📧 Contacta al equipo en el canal de Slack #documentation

