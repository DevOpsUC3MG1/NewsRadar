# Account Verification and Password Reset Endpoints

Los siguientes endpoints han sido implementados para la verificación de cuenta y recuperación de contraseña:

## Nuevos Endpoints

### 1. Verificar Cuenta
**POST** `/api/v1/auth/verify`

Verifica la cuenta usando el token recibido por email durante el registro.

**Request:**
```json
{
  "token": "uuid-token-string"
}
```

**Response (201):**
```json
{
  "message": "Cuenta verificada exitosamente",
  "success": true
}
```

---

### 2. Reenviar Email de Verificación
**POST** `/api/v1/auth/resend-verification`

Reenvía el email de verificación a un usuario que aún no ha verificado su cuenta.

**Request:**
```json
"user@email.com"
```

**Response:**
```json
{
  "message": "Email de verificación reenviado",
  "success": true
}
```

---

### 3. Solicitar Reset de Contraseña
**POST** `/api/v1/auth/password-reset-request`

Genera un token de reset y envía un email al usuario (por seguridad, no revela si el email existe).

**Request:**
```json
{
  "email": "user@email.com"
}
```

**Response:**
```json
{
  "message": "Si el email existe en el sistema, recibirá un enlace para resetear la contraseña",
  "success": true
}
```

---

### 4. Confirmar Reset de Contraseña
**POST** `/api/v1/auth/password-reset`

Confirma el reset de contraseña usando el token recibido por email.

**Request:**
```json
{
  "token": "uuid-token-string",
  "new_password": "NewPassword123!"
}
```

**Response:**
```json
{
  "message": "Contraseña reseteada exitosamente",
  "success": true
}
```

---

## Cambios en el Modelo de Usuario

Se han añadido los siguientes campos a la tabla `users`:

- `is_verified` (Boolean, default: False) - Indica si la cuenta ha sido verificada
- `verification_token` (String, nullable) - Token para verificación de cuenta
- `password_reset_token` (String, nullable) - Token para reset de contraseña  
- `password_reset_expiry` (DateTime, nullable) - Expiración del token de reset (1 hora)

## Flujo Recomendado para Frontend

### Registro y Verificación
1. Usuario se registra vía `POST /api/v1/auth/register`
2. Recibe email con token de verificación
3. Hace clic en el enlace que lleva a página de verificación
4. Frontend llama a `POST /api/v1/auth/verify` con el token
5. Frontend muestra confirmación de éxito

### Recuperación de Contraseña
1. Usuario solicita reset vía `POST /api/v1/auth/password-reset-request` 
2. Recibe email con token de reset
3. Hace clic en el enlace que lleva a página de cambio de contraseña
4. Frontend llama a `POST /api/v1/auth/password-reset` con token + nueva contraseña
5. Frontend muestra confirmación de éxito

## Migración de Base de Datos

Se ha creado una migración de Alembic en `backend/migrations/versions/001_add_verification_fields.py` 
que añade los campos nuevos a la tabla existente.

Para ejecutar la migración:
```bash
cd backend
alembic upgrade head
```

O ejecutar `init_db.py` que crea todas las tablas desde cero.

## TODOs Pendientes

En los nuevos endpoints hay comentarios `# TODO:` donde se deben implementar:
- Funciones para enviar emails con tokens
- Integración con servicio de correo (SendGrid, AWS SES, etc.)

Esto se ha marcado intencionalmente para que el equipo pueda implementarlo con su servicio de mail elegido.
