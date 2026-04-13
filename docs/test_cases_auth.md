# Casos de Prueba - Autenticación y Usuarios (Sprint 1)

## 1. Módulo de Registro (POST `/register`)
| ID | Nombre del Caso | Acción (Lo que hacemos) | Resultado Esperado (Lo que debe pasar) |
| :--- | :--- | :--- | :--- |
| **AUTH-01** | Registro exitoso | Enviar JSON con email válido y contraseña segura. | Código `201 Created`. El usuario se guarda en BD. |
| **AUTH-02** | Email duplicado | Intentar registrar un email que ya existe en la BD. | Código `400 Bad Request`. Mensaje: "Email ya registrado". |
| **AUTH-03** | Email inválido | Enviar un email sin el formato correcto (ej: `pepito.com`). | Código `422 Unprocessable Entity` (Fallo de validación Pydantic). |
| **AUTH-04** | Contraseña débil | Enviar una contraseña de menos de 8 caracteres. | Código `422 Unprocessable Entity`. |

## 2. Módulo de Login (POST `/login`)
| ID | Nombre del Caso | Acción (Lo que hacemos) | Resultado Esperado (Lo que debe pasar) |
| :--- | :--- | :--- | :--- |
| **AUTH-05** | Login exitoso | Enviar credenciales correctas. | Código `200 OK`. Devuelve un `access_token` (JWT). |
| **AUTH-06** | Contraseña incorrecta| Enviar un email válido pero contraseña errónea. | Código `401 Unauthorized`. |
| **AUTH-07** | Usuario no existe | Enviar un email que no está en la base de datos. | Código `401 Unauthorized`. |

## 3. Roles y Permisos (RF-09)
| ID | Nombre del Caso | Acción (Lo que hacemos) | Resultado Esperado (Lo que debe pasar) |
| :--- | :--- | :--- | :--- |
| **AUTH-08** | Acceso sin Token | Intentar acceder a `/users/me` sin enviar el header Authorization. | Código `401 Unauthorized`. |
| **AUTH-09** | Bloqueo a Lector | Un usuario con rol "Lector" intenta acceder a una ruta de Gestor. | Código `403 Forbidden`. |