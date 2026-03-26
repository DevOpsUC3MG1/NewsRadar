# Estrategia de QA - NewsRadar

## 1. Herramientas
- **Framework:** Pytest
- **Cobertura:** pytest-cov (Objetivo: >70%)
- **Integración Continua:** GitHub Actions ejecutan los tests en cada Push.

## 2. Tipos de Pruebas
- **Unitarias:** Validación de lógica, modelos Pydantic y utilidades.
- **Integración:** Endpoints de FastAPI y conexión con BD.
- **E2E:** Flujos completos (Registro -> Login -> Alerta).

## 3. Verificaciones Críticas (Anexo I)
Se realizarán pruebas manuales y automáticas sobre:
- Roles de usuario (Lector vs Gestor).
- Notificaciones por email.
- Clasificación IPTC de noticias.