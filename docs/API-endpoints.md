# API Endpoints - NewsRadar

## Base URL
```
http://localhost:8000/api/v1
```

## Autenticación
Todos los endpoints excepto `/auth/*` requieren autenticación con token Bearer:
```
Authorization: Bearer <access_token>
```

---

## 🔐 Autenticación (Auth)

### Registro de Usuario
```http
POST /auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "user@example.com",
  "password": "Password123!",
  "first_name": "string",
  "last_name": "string",
  "organization": "string",
  "role_ids": [1, 2]
}
```
**Respuestas:**
- `201 Created`: Usuario registrado. Email de verificación enviado
- `400 Bad Request`: Email duplicado
- `422 Unprocessable Entity`: Validación fallida (email inválido, contraseña débil, etc.)

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "Password123!"
}
```
**Respuestas:**
- `200 OK`: `{"access_token": "uuid-token", "token_type": "bearer"}`
- `401 Unauthorized`: Credenciales inválidas

### Verificar Cuenta
```http
POST /auth/verify
Content-Type: application/json

{
  "token": "verification-token-from-email"
}
```
**Respuestas:**
- `200 OK`: Cuenta verificada exitosamente
- `404 Not Found`: Token inválido o expirado
- `400 Bad Request`: Cuenta ya verificada

### Reenviar Email de Verificación
```http
POST /auth/resend-verification
Content-Type: application/json

{
  "email": "user@example.com"
}
```
**Respuestas:**
- `200 OK`: Email de verificación reenviado
- `404 Not Found`: Usuario no encontrado
- `400 Bad Request`: Cuenta ya verificada

### Solicitar Recuperación de Contraseña
```http
POST /auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```
**Respuestas:**
- `200 OK`: Email de recuperación enviado (respuesta genérica por seguridad)

### Restablecer Contraseña
```http
POST /auth/reset-password
Content-Type: application/json

{
  "token": "reset-token-from-email",
  "new_password": "NewPassword123!"
}
```
**Respuestas:**
- `200 OK`: Contraseña restablecida
- `400 Bad Request`: Token inválido o expirado
- `422 Unprocessable Entity`: Contraseña débil

---

## 👥 Usuarios (Users)

### Listar Usuarios
```http
GET /users
Authorization: Bearer <token>
```
**Respuestas:**
- `200 OK`: `[{id, email, first_name, last_name, organization, role_ids}, ...]`
- `401 Unauthorized`: Token inválido

### Crear Usuario (Admin)
```http
POST /users
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "Password123!",
  "first_name": "string",
  "last_name": "string",
  "organization": "string",
  "role_ids": [1]
}
```
**Respuestas:**
- `201 Created`: Usuario creado
- `409 Conflict`: Email duplicado

### Obtener Usuario
```http
GET /users/{user_id}
Authorization: Bearer <token>
```
**Respuestas:**
- `200 OK`: `{id, email, first_name, last_name, organization, role_ids}`
- `404 Not Found`: Usuario no encontrado

### Actualizar Usuario
```http
PUT /users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "first_name": "newname",
  "password": "NewPassword123!",
  ...
}
```
**Respuestas:**
- `200 OK`: Usuario actualizado
- `404 Not Found`: Usuario no encontrado
- `409 Conflict`: Email duplicado

### Eliminar Usuario
```http
DELETE /users/{user_id}
Authorization: Bearer <token>
```
**Respuestas:**
- `204 No Content`: Usuario eliminado
- `404 Not Found`: Usuario no encontrado

---

## 🎯 Roles (Roles)

### Listar Roles
```http
GET /roles
Authorization: Bearer <token>
```
**Respuestas:**
- `200 OK`: `[{id, name}, ...]`

### Crear Rol
```http
POST /roles
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Editor"
}
```
**Respuestas:**
- `201 Created`: `{id, name}`

### Obtener Rol
```http
GET /roles/{role_id}
Authorization: Bearer <token>
```
**Respuestas:**
- `200 OK`: `{id, name}`
- `404 Not Found`: Rol no encontrado

### Actualizar Rol
```http
PUT /roles/{role_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Moderator"
}
```
**Respuestas:**
- `200 OK`: Rol actualizado
- `404 Not Found`: Rol no encontrado

### Eliminar Rol
```http
DELETE /roles/{role_id}
Authorization: Bearer <token>
```
**Respuestas:**
- `204 No Content`: Rol eliminado
- `409 Conflict`: Rol asignado a usuarios

---

## 🔔 Alertas (Alerts)

### Listar Alertas del Usuario
```http
GET /users/{user_id}/alerts
Authorization: Bearer <token>
```
**Respuestas:**
- `200 OK`: `[{id, name, descriptors, categories, cron_expression, user_id}, ...]`
- `404 Not Found`: Usuario no encontrado

### Crear Alerta
```http
POST /users/{user_id}/alerts
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Alerta Tecnológica",
  "descriptors": ["IA", "Machine Learning"],
  "categories": [
    {"code": "01000000", "label": "Economía"}
  ],
  "cron_expression": "0 * * * *"
}
```
**Respuestas:**
- `201 Created`: Alerta creada
- `403 Forbidden`: Usuario no tiene rol Gestor
- `404 Not Found`: Usuario no encontrado

### Obtener Alerta
```http
GET /users/{user_id}/alerts/{alert_id}
Authorization: Bearer <token>
```
**Respuestas:**
- `200 OK`: `{id, name, descriptors, categories, cron_expression, user_id}`
- `404 Not Found`: Alerta no encontrada

### Actualizar Alerta
```http
PUT /users/{user_id}/alerts/{alert_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Alerta Actualizada",
  "descriptors": ["nuevos", "términos"]
}
```
**Respuestas:**
- `200 OK`: Alerta actualizada
- `404 Not Found`: Alerta no encontrada

### Eliminar Alerta
```http
DELETE /users/{user_id}/alerts/{alert_id}
Authorization: Bearer <token>
```
**Respuestas:**
- `204 No Content`: Alerta eliminada
- `404 Not Found`: Alerta no encontrada

---

## 📢 Notificaciones (Notifications)

### Listar Notificaciones de Alerta
```http
GET /users/{user_id}/alerts/{alert_id}/notifications
Authorization: Bearer <token>
```
**Respuestas:**
- `200 OK`: `[{id, alert_id, timestamp, metrics}, ...]`
- `404 Not Found`: Alerta no encontrada

### Crear Notificación
```http
POST /users/{user_id}/alerts/{alert_id}/notifications
Authorization: Bearer <token>
Content-Type: application/json

{
  "timestamp": "2026-04-23T10:30:00Z",
  "metrics": [
    {"name": "noticias_encontradas", "value": 5},
    {"name": "relevancia_promedio", "value": 0.85}
  ]
}
```
**Respuestas:**
- `201 Created`: Notificación creada
- `404 Not Found`: Alerta no encontrada

### Obtener Notificación
```http
GET /users/{user_id}/alerts/{alert_id}/notifications/{notification_id}
Authorization: Bearer <token>
```
**Respuestas:**
- `200 OK`: `{id, alert_id, timestamp, metrics}`
- `404 Not Found`: Notificación no encontrada

### Actualizar Notificación
```http
PUT /users/{user_id}/alerts/{alert_id}/notifications/{notification_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "metrics": [
    {"name": "noticias_encontradas", "value": 8}
  ]
}
```
**Respuestas:**
- `200 OK`: Notificación actualizada
- `404 Not Found`: Notificación no encontrada

### Eliminar Notificación
```http
DELETE /users/{user_id}/alerts/{alert_id}/notifications/{notification_id}
Authorization: Bearer <token>
```
**Respuestas:**
- `204 No Content`: Notificación eliminada
- `404 Not Found`: Notificación no encontrada

---

## 📂 Categorías (Categories)

### Listar Categorías
```http
GET /categories
Authorization: Bearer <token>
```
**Respuestas:**
- `200 OK`: `[{id, name, source}, ...]`

### Crear Categoría
```http
POST /categories
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Tecnología",
  "source": "IPTC"
}
```
**Respuestas:**
- `201 Created`: Categoría creada
- `422 Unprocessable Entity`: Source no es "IPTC"

### Obtener Categoría
```http
GET /categories/{category_id}
Authorization: Bearer <token>
```
**Respuestas:**
- `200 OK`: `{id, name, source}`
- `404 Not Found`: Categoría no encontrada

### Actualizar Categoría
```http
PUT /categories/{category_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Ciencia y Tecnología"
}
```
**Respuestas:**
- `200 OK`: Categoría actualizada
- `404 Not Found`: Categoría no encontrada

### Eliminar Categoría
```http
DELETE /categories/{category_id}
Authorization: Bearer <token>
```
**Respuestas:**
- `204 No Content`: Categoría eliminada
- `409 Conflict`: Categoría asociada a canales RSS

---

## 📡 Fuentes de Información (Information Sources)

### Listar Fuentes
```http
GET /information-sources
Authorization: Bearer <token>
```
**Respuestas:**
- `200 OK`: `[{id, name, url}, ...]`

### Crear Fuente
```http
POST /information-sources
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "El País",
  "url": "https://elpais.com"
}
```
**Respuestas:**
- `201 Created`: Fuente creada
- `422 Unprocessable Entity`: URL inválida

### Obtener Fuente
```http
GET /information-sources/{source_id}
Authorization: Bearer <token>
```
**Respuestas:**
- `200 OK`: `{id, name, url}`
- `404 Not Found`: Fuente no encontrada

### Actualizar Fuente
```http
PUT /information-sources/{source_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "El País Digital"
}
```
**Respuestas:**
- `200 OK`: Fuente actualizada
- `404 Not Found`: Fuente no encontrada

### Eliminar Fuente
```http
DELETE /information-sources/{source_id}
Authorization: Bearer <token>
```
**Respuestas:**
- `204 No Content`: Fuente eliminada

---

## 🔗 Canales RSS (RSS Channels)

### Listar Canales RSS
```http
GET /information-sources/{source_id}/rss-channels
Authorization: Bearer <token>
```
**Respuestas:**
- `200 OK`: `[{id, url, category_id, information_source_id}, ...]`
- `404 Not Found`: Fuente no encontrada

### Crear Canal RSS
```http
POST /information-sources/{source_id}/rss-channels
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://elpais.com/rss/politica.xml",
  "category_id": 1
}
```
**Respuestas:**
- `201 Created`: Canal creado
- `404 Not Found`: Fuente no encontrada

### Obtener Canal RSS
```http
GET /information-sources/{source_id}/rss-channels/{channel_id}
Authorization: Bearer <token>
```
**Respuestas:**
- `200 OK`: `{id, url, category_id, information_source_id}`
- `404 Not Found`: Canal no encontrado

### Actualizar Canal RSS
```http
PUT /information-sources/{source_id}/rss-channels/{channel_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "category_id": 2
}
```
**Respuestas:**
- `200 OK`: Canal actualizado
- `404 Not Found`: Canal no encontrado

### Eliminar Canal RSS
```http
DELETE /information-sources/{source_id}/rss-channels/{channel_id}
Authorization: Bearer <token>
```
**Respuestas:**
- `204 No Content`: Canal eliminado

---

## 📊 Sistema (System)

### Health Check
```http
GET /health
```
**Respuestas:**
- `200 OK`: `{"status": "ok", "timestamp": "2026-04-23T10:30:00Z"}`

---

## Códigos de Estado HTTP

| Código | Significado |
|--------|------------|
| `200` | OK - Solicitud exitosa |
| `201` | Created - Recurso creado |
| `204` | No Content - Eliminación exitosa |
| `400` | Bad Request - Datos inválidos |
| `401` | Unauthorized - Token inválido/ausente |
| `403` | Forbidden - Acceso denegado por permisos |
| `404` | Not Found - Recurso no encontrado |
| `409` | Conflict - Violación de constraints (ej: email duplicado) |
| `422` | Unprocessable Entity - Validación Pydantic fallida |

---

## Ejemplo Completo: Flujo de Uso

1. **Registrarse**
   ```bash
   POST /auth/register
   → Email de verificación enviado
   ```

2. **Verificar Cuenta**
   ```bash
   POST /auth/verify
   → Cuenta verificada
   ```

3. **Login**
   ```bash
   POST /auth/login
   → Recibe token
   ```

4. **Crear Alerta**
   ```bash
   POST /users/1/alerts
   → Alerta creada
   ```

5. **Ver Notificaciones**
   ```bash
   GET /users/1/alerts/1/notifications
   → Listado de notificaciones
   ```

---

## Documentación Interactiva

Accede a Swagger UI en:
```
http://localhost:8000/docs
```

O a ReDoc en:
```
http://localhost:8000/redoc
```

