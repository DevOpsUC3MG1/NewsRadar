# ADR-003: Estrategia de Feature Flags para la Competición

## Estado
Aceptado

## Fecha
2026-03-21

## Contexto
El sistema NewsRadar debe participar en una competición técnica el 25 de mayo. El "playbook" de la competición exige que el equipo sea capaz de activar, desactivar o modificar funcionalidades (ej. cambiar el motor de IA, desactivar notificaciones o añadir nuevas fuentes RSS) en tiempo real. 

El objetivo es alcanzar un **tiempo de respuesta < 2 minutos** sin realizar nuevos despliegues ni reiniciar los contenedores de Docker.

## Decisión
Se implementará un sistema de **Configuración Dinámica (Feature Flags)** basado en las siguientes piezas:

1. **Almacenamiento:** Una tabla en PostgreSQL denominada `config_flags` con los campos `key` (string), `value` (boolean/json) y `description`.
2. **Capa de Aplicación:** Un servicio `ConfigProvider` en FastAPI que implementa el patrón *Singleton*. Este servicio consultará la base de datos y mantendrá los valores en memoria para evitar latencia.
3. **Control:** Un endpoint protegido `PATCH /api/v1/config` que permite al administrador del equipo cambiar cualquier flag de forma instantánea.

## Consecuencias

**Positivas:**
- **Agilidad extrema:** Cumplimos con creces el requisito de los 2 minutos del "combate".
- **Resiliencia:** Si un servicio externo (como la API de OpenAI) falla o agota el presupuesto, podemos desactivar la generación de sinónimos al instante sin que la API devuelva errores 500.
- **Pruebas en vivo:** Permite activar módulos de depuración en caliente si detectamos comportamientos extraños durante la demo.

**Negativas / Riesgos:**
- **Deuda técnica:** El código se llena de condicionales `if config.is_enabled("feature_x")`, lo que requiere una limpieza tras la competición.
- **Complejidad de pruebas:** Los tests de integración ahora deben probar el sistema con los flags tanto en `true` como en `false`.

## Ejemplo práctico
Durante la competición, el profesor pide desactivar el envío de correos porque el servidor SMTP está saturado. El equipo ejecuta:

```bash
curl -X PATCH "[https://api.newsradar.com/api/v1/config](https://api.newsradar.com/api/v1/config)" \
     -H "Authorization: Bearer <admin_token>" \
     -d '{"flag": "email_notifications", "status": false}'
