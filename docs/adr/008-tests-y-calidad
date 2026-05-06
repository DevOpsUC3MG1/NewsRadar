# ADR-008: Estrategia de Calidad y Testing

## Estado
Aceptado

## Contexto
Dada la importancia de la estabilidad en la competición del 25 de mayo, se requiere una cobertura de tests que garantice que los cambios rápidos (Hotfixes) no rompan funcionalidades críticas.

## Decisión
Se implementa una pirámide de pruebas automatizada:
1. **Tests Unitarios (Pytest):** Cobertura > 70% en la lógica de negocio (servicios de clasificación e IA).
2. **Tests de Integración:** Verificación de los contratos de la API (Anexo I) simulando llamadas reales a la base de datos (usando una BD de test en Docker).
3. **Calidad de Código:** Uso de **Ruff** (Linter) y **SonarQube** para detectar deuda técnica y vulnerabilidades de seguridad antes del merge.

## Consecuencias
- **Positivas:** Alta confianza durante la competición. Si un test falla en el pipeline de GitHub Actions, no se permite el despliegue.
- **Negativas:** Aumenta el tiempo de desarrollo inicial al tener que mantener la suite de pruebas.