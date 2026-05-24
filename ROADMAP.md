# Roadmap — NewsRadar

## Hito 1: MVP funcional (completado)

- [x] Stack: FastAPI + PostgreSQL + MongoDB + React + Docker
- [x] Autenticación (registro, login, JWT, verificación email)
- [x] RBAC (Gestor / Lector)
- [x] CRUD de alertas con categorías IPTC
- [x] CRUD de fuentes y canales RSS
- [x] CRUD de usuarios y roles
- [x] Dashboard con nubes de palabras
- [x] Notificaciones y estadísticas (MongoDB)
- [x] Internacionalización ES/EN
- [x] CI/CD con GitHub Actions
- [x] Tests automatizados (141 tests, 50%+ cobertura)

## Hito 2: Calidad y documentación (completado)

- [x] Pirámide de tests (unitarios + integración + E2E)
- [x] ADRs (8 registros de decisiones)
- [x] Documentación técnica (requisitos, modelo datos, API, frontend)
- [x] Diagramas de arquitectura (C4, despliegue)
- [x] Generación automática de documentación (pdoc)
- [x] Linting (flake8 + ESLint + Ruff)
- [x] Scripts de construcción, test, deploy, rollback, seed

## Hito 3: Competición 25 de mayo (en curso)

- [ ] Validar CI/CD con push a GHCR
- [ ] Verificar cobertura ≥ 50%
- [ ] Probar despliegue one-click en entorno limpio
- [ ] Ejecutar suite completa de tests
- [ ] Revisar playbook de competición

## Hito 4: Post-competición (futuro)

- [ ] Cobertura ≥ 70%
- [ ] Ruff como linter/formatter principal
- [ ] pyproject.toml consolidado
- [ ] Despliegue con Nginx + SSL
- [ ] Monitorización con Prometheus + Grafana
- [ ] Worker RSS con Celery
