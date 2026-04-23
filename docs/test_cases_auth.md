# Casos de Prueba - Autenticación y Usuarios

## 1. Módulo de Registro (POST `/api/v1/auth/register`)

| ID | Nombre del Caso | Acción | Resultado Esperado | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **AUTH-01** | Registro exitoso | Enviar JSON con email válido, contraseña (mín 6 caracteres), nombre, apellido, organización | 201 Created. Usuario se guarda en BD. Email de verificación enviado | ✅ Implementado |
| **AUTH-02** | Email duplicado | Registrar dos usuarios con el mismo email | 409 Conflict. Mensaje: "El email ya está registrado" | ✅ Implementado |
| **AUTH-03** | Email inválido | Enviar email sin formato correcto (ej: `pepito.com`) | 422 Unprocessable Entity (validación Pydantic EmailStr) | ✅ Implementado |
| **AUTH-04** | Contraseña débil | Enviar contraseña menor a 6 caracteres | 422 Unprocessable Entity | ✅ Implementado |
| **AUTH-05** | Campos obligatorios faltantes | No enviar email o contraseña en payload | 422 Unprocessable Entity | ✅ Implementado |

## 2. Módulo de Login (POST `/api/v1/auth/login`)

| ID | Nombre del Caso | Acción | Resultado Esperado | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **AUTH-06** | Login exitoso | Enviar credenciales correctas | 200 OK. Devuelve `access_token` (JWT Bearer) | ✅ Implementado |
| **AUTH-07** | Contraseña incorrecta | Email válido pero contraseña errónea | 401 Unauthorized | ✅ Implementado |
| **AUTH-08** | Usuario no existe | Email que no está en la BD | 401 Unauthorized | ✅ Implementado |
| **AUTH-09** | Email inválido en login | Enviar email con formato incorrecto | 422 Unprocessable Entity | ✅ Implementado |

## 3. Verificación de Cuenta (POST `/api/v1/auth/verify`)

| ID | Nombre del Caso | Acción | Resultado Esperado | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **AUTH-10** | Verificación exitosa | Enviar token válido recibido por email | 200 OK. `is_verified = true`. Mensaje de éxito | ✅ Implementado |
| **AUTH-11** | Token inválido | Enviar token que no existe o expiró | 404 Not Found. "Token de verificación inválido o expirado" | ✅ Implementado |
| **AUTH-12** | Cuenta ya verificada | Intentar verificar una cuenta ya verificada | 400 Bad Request. "La cuenta ya ha sido verificada" | ✅ Implementado |

## 4. Reenvío de Verificación (POST `/api/v1/auth/resend-verification`)

| ID | Nombre del Caso | Acción | Resultado Esperado | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **AUTH-13** | Reenvío exitoso | Solicitar reenvío con email válido y no verificado | 200 OK. Nuevo email enviado con token regenerado | ✅ Implementado |
| **AUTH-14** | Cuenta ya verificada | Intentar reenvío a cuenta ya verificada | 400 Bad Request. "La cuenta ya está verificada" | ✅ Implementado |
| **AUTH-15** | Usuario no encontrado | Email que no existe en BD | 404 Not Found. "Usuario no encontrado" | ✅ Implementado |

## 5. Recuperación de Contraseña (POST `/api/v1/auth/forgot-password`)

| ID | Nombre del Caso | Acción | Resultado Esperado | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **AUTH-16** | Solicitud exitosa | Email válido de usuario existente | 200 OK. Email de recuperación enviado. Mensaje genérico (no revelar si existe) | ✅ Implementado |
| **AUTH-17** | Email no existe | Email que no está registrado | 200 OK. Respuesta genérica (seguridad: no revelar existencia) | ✅ Implementado |

## 6. Restablecimiento de Contraseña (POST `/api/v1/auth/reset-password`)

| ID | Nombre del Caso | Acción | Resultado Esperado | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **AUTH-18** | Reset exitoso | Enviar token válido + nueva contraseña (mín 6 caracteres) | 200 OK. Contraseña actualizada. Token invalidado | ✅ Implementado |
| **AUTH-19** | Token inválido | Token inexistente o expirado | 400 Bad Request. "Token de recuperación inválido o expirado" | ✅ Implementado |
| **AUTH-20** | Contraseña débil en reset | Nueva contraseña menor a 6 caracteres | 422 Unprocessable Entity | ✅ Implementado |

## 7. Protección de Endpoints (Autenticación)

| ID | Nombre del Caso | Acción | Resultado Esperado | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **AUTH-21** | Acceso sin Token | Intentar acceder a endpoint protegido (`/users/me`) sin header Authorization | 401 Unauthorized. "Token inválido o ausente" | ✅ Implementado |
| **AUTH-22** | Token inválido | Enviar token que no existe en `active_tokens` | 401 Unauthorized. "Token inválido o expirado" | ✅ Implementado |
| **AUTH-23** | Token mal formado | Header con esquema incorrecto (ej: "Basic token") | 401 Unauthorized | ✅ Implementado |

## 8. Roles y Permisos (RF-02)

| ID | Nombre del Caso | Acción | Resultado Esperado | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **AUTH-24** | Bloqueo a Lector | Usuario con rol "Lector" intenta crear alerta | 403 Forbidden (solo Gestor puede) | ✅ Implementado |
| **AUTH-25** | Permiso a Gestor | Usuario con rol "Gestor" puede crear alerta | 201 Created | ✅ Implementado |
| **AUTH-26** | Múltiples roles | Usuario con múltiples roles tiene acceso a todos | 200 OK. Acceso según roles asignados | ✅ Implementado |

## 9. Gestión de Usuarios (GET/POST/PUT `/api/v1/users*`)

| ID | Nombre del Caso | Acción | Resultado Esperado | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **USER-01** | Listar usuarios | GET `/api/v1/users` con token válido | 200 OK. Array de usuarios sin contraseñas | ✅ Implementado |
| **USER-02** | Obtener usuario | GET `/api/v1/users/{user_id}` | 200 OK. Datos del usuario (sin password) | ✅ Implementado |
| **USER-03** | Usuario no encontrado | GET con `user_id` inexistente | 404 Not Found | ✅ Implementado |
| **USER-04** | Actualizar usuario | PUT `/api/v1/users/{user_id}` con datos parciales | 200 OK. Usuario actualizado (solo campos permitidos) | ✅ Implementado |
| **USER-05** | Email duplicado en update | UPDATE con email que ya existe en otro usuario | 409 Conflict | ✅ Implementado |

## Notas de Implementación

- **Esquema Bearer:** Todos los endpoints protegidos usan `Authorization: Bearer <token>`
- **Almacenamiento de tokens:** En memoria para pruebas (en producción usar Redis con TTL)
- **Envío de emails:** Configurado con Gmail + contraseña de aplicación
- **Validación:** Automática con modelos Pydantic
- **Cliente de pruebas:** TestClient de FastAPI sin hacer llamadas HTTP reales