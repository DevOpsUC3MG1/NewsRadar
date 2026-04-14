# ADR-002: Autenticación y Autorización con JWT y Roles

## Estado
Aceptado

## Fecha
2026-03-14

## Contexto
El sistema requiere gestión de usuarios con dos roles diferenciados:
- **Gestor de NewsRadar**: puede crear y gestionar alertas y fuentes RSS.
- **Lector**: acceso de solo lectura a toda la plataforma.
- **Administrador**: usuario inicial capaz de asignar roles a nuevos usuarios.

Además el enunciado exige:
- Registro con verificación de email (caducidad 24 horas).
- Recuperación de contraseña.
- Control estricto de acceso: el Lector no puede gestionar alertas bajo
  ninguna circunstancia (es una de las 7 inspecciones manuales del Anexo I).

Las opciones evaluadas fueron:

**Mecanismo de autenticación:**
- JWT (JSON Web Tokens) vs sesiones en servidor vs OAuth2 externo (Google, GitHub)

**Gestión de roles:**
- Roles en tabla de BD (RBAC) vs claims directamente en el token JWT
  vs sistema de permisos granular (PBAC)

**Hash de contraseñas:**
- bcrypt vs argon2 vs scrypt

## Decisión

**JWT con OAuth2PasswordBearer** para autenticación, integrado de forma
nativa en FastAPI.

**RBAC (Role-Based Access Control)** con roles almacenados en PostgreSQL
y propagados al token JWT como claims.

**bcrypt** para hash de contraseñas mediante passlib.

El flujo completo es el siguiente:

POST /auth/register → crea usuario (is_verified=False) → envía email con token
GET  /auth/verify/{token} → activa cuenta (is_verified=True, caduca en 24h)
POST /auth/login → valida credenciales → devuelve access_token (JWT, 30min)
+ refresh_token (JWT, 7 días)
Requests autenticados → header: Authorization: Bearer <access_token>
Middleware de roles → verifica claim "role" del token → permite o rechaza

La estructura del payload JWT es:
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "gestor_newsradar",
  "exp": 1234567890
}
```

**JWT** se elige sobre sesiones en servidor porque:
- FastAPI está diseñado para trabajar con JWT a través de OAuth2PasswordBearer,
  reduciendo el código necesario al mínimo.
- Sin estado en servidor: escala mejor y simplifica el despliegue en Docker.
- El token puede transportar el rol del usuario evitando una consulta a BD
  en cada request para verificar permisos.

**Roles en BD** (además de en el token) se eligen sobre solo claims en JWT porque:
- Permite revocar o cambiar roles sin esperar a que expire el token.
- El administrador puede asignar roles a nuevos usuarios desde la interfaz,
  requisito explícito del enunciado.
- La tabla user_roles permite auditoría y trazabilidad de cambios de rol.

**bcrypt** se elige sobre argon2 porque:
- passlib con bcrypt es la combinación más documentada con FastAPI.
- Coste computacional configurable (rounds) suficiente para el caso de uso.

## Consecuencias

**Positivas:**
- La verificación de rol en cada endpoint se reduce a un decorador/dependencia
  de FastAPI: `Depends(require_role("gestor_newsradar"))`.
- La inspección manual INS-03 (el lector no puede gestionar alertas) queda
  cubierta de forma centralizada en el middleware, no endpoint por endpoint.
- El email de verificación con caducidad de 24h se implementa con un token
  firmado con fecha de expiración, sin tabla adicional en BD.

**Negativas / riesgos:**
- Si un usuario es degradado de Gestor a Lector, su token JWT sigue siendo
  válido hasta que expire (máx. 30 minutos). Mitigación: el middleware
  también consulta el rol actual en BD para operaciones críticas.
- El refresh token debe almacenarse en BD (tabla refresh_tokens) para poder
  invalidarlo en caso de logout o cambio de contraseña.
- El envío de emails de verificación requiere configuración SMTP correcta
  en producción (variables en .env).

## Tablas de BD implicadas

users         → id, email, nombre, apellidos, organización,
password_hash, is_verified, created_at
roles         → id, name (gestor_newsradar | lector | admin)
user_roles    → user_id FK, role_id FK
refresh_tokens → id, user_id FK, token_hash, expires_at, revoked

## Referencias
- Requisitos relacionados: RF-09, RF-10, RF-11, RNF-03
- Inspección manual: INS-02 (email verificación), INS-03 (lector sin gestión)
- Enunciado sección 3.1: Gestión de usuarios
- Componentes afectados:
  - `backend/app/routers/auth.py`
  - `backend/app/routers/users.py`
  - `backend/app/middleware/auth.py`
  - `backend/app/services/email_service.py`
- Ver también: ADR-001 (stack tecnológico)
