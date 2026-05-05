# Plan de Pruebas: Gestión de Términos y Canales

| ID Requisito | Descripción | Prioridad |
| :--- | :--- | :--- |
| RF-01 | Gestión de Alertas (máx. 20) | Alta |
| RF-02 | Expansión de descriptores con IA | Alta |
| RF-03 | Programación cron de alertas | Alta |
| RF-04 | Selección de fuentes por alerta | Media |
| RF-05 | Clasificación IPTC de noticias | Alta |

---

## 1. Casos de Prueba: Gestión de Alertas (Términos)

### CP-ALT-01: Creación de Alerta Exitosa con IA
**Objetivo:** Validar que el flujo completo de creación genera descriptores y guarda la alerta.
- **Precondición:** Usuario autenticado con rol `Gestor`.
- **Pasos:**
    1. Acceder a `/alerts` y pulsar "Nueva Alerta".
    2. Introducir Nombre: "Crisis Ucrania", Palabra Clave: "guerra", Cron: `0 12 * * *`.
    3. Pulsar "Generar Descriptores".
- **Resultado Esperado:** - El sistema muestra entre 3 y 10 términos sugeridos (ej: conflicto, invasión, OTAN).
    - Al confirmar, la alerta se guarda en PostgreSQL y es visible en la lista.

### CP-ALT-02: Control de Límite de Alertas
**Objetivo:** Verificar que el sistema impide crear más de 20 alertas por usuario.
- **Precondición:** El usuario ya tiene 20 alertas creadas.
- **Pasos:**
    1. Intentar crear una alerta número 21.
- **Resultado Esperado:** - Error `400 Bad Request` con mensaje "Límite de alertas alcanzado (máx. 20)".

### CP-ALT-03: Validación de Expresión Cron
**Objetivo:** Asegurar que solo se aceptan formatos cron válidos.
- **Pasos:**
    1. Introducir una expresión inválida: `esto-no-es-un-cron`.
- **Resultado Esperado:** - Error de validación en el formulario (Frontend) o error `422` (Backend).

---

## 2. Casos de Prueba: Gestión de Canales (Fuentes)

### CP-CAN-01: Carga Masiva de Fuentes (Script Seed)
**Objetivo:** Validar que el sistema inicia con la base de datos de canales requerida.
- **Pasos:**
    1. Ejecutar `./scripts/seed.sh` en un entorno limpio.
    2. Consultar la tabla `sources` en la base de datos.
- **Resultado Esperado:** - Se han cargado exactamente 100 canales RSS con sus respectivas categorías IPTC.

### CP-CAN-02: Selección de Fuentes Específicas
**Objetivo:** Validar el RF-04 (vincular alerta a fuentes concretas).
- **Pasos:**
    1. Crear una alerta.
    2. En la sección "Fuentes", desmarcar "Todas" y seleccionar manualmente 2 canales de "El País".
- **Resultado Esperado:** - La configuración se persiste correctamente en la base de datos de alertas.

---

## 3. Pruebas de Integración: Worker y Procesamiento

### CP-WRK-01: Ciclo de Vida de una Noticia (End-to-End)
**Objetivo:** Validar que el worker detecta noticias y las clasifica.
- **Precondición:** Existe una alerta activa para "Ciberseguridad" y el `rss_worker` está en marcha.
- **Pasos:**
    1. Inyectar un feed RSS falso (`feed_falso.xml`) que contenga una noticia con la palabra "Hacker".
    2. Esperar a la ejecución del worker.
- **Resultado Esperado:** - La noticia se guarda en MongoDB.
    - La noticia tiene asignada la categoría IPTC "04000000 (Economía, negocios y finanzas)" o la que corresponda al canal.
    - Se registra el envío de un email de notificación (simulado en logs).

---

## 4. Matriz de Trazabilidad (Tester)

| Caso de Prueba | RF Validado | Estado (Manual) | Estado (Auto) |
| :--- | :--- | :--- | :--- |
| CP-ALT-01 | RF-01, RF-02 | Pendiente | `test_alertas.py` |
| CP-ALT-02 | RF-01 | Pendiente | `test_logic.py` |
| CP-ALT-03 | RF-03 | Pendiente | `test_setup.py` |
| CP-CAN-01 | RF-04 | Pendiente | `test_db_connection.py`|
| CP-WRK-01 | RF-05, RF-06 | Pendiente | `test_worker_rss.py` |s