from __future__ import annotations

import asyncio
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from sqlalchemy import select, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db, engine, Base
from .database_mongodb import get_mongo_db
from .models import User as UserModel, Role as RoleModel, Alert as AlertModel
from .models import Category as CategoryModel, InformationSource as InformationSourceModel
from .models import RSSChannel as RSSChannelModel
from .services.ia_service import generate_synonyms, classify_iptc_level1
from .services.rss_worker import RSSWorker

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = FastAPI(
    title="NewsRadar API",
    version="1.0.0",
    description="API REST para gestión de usuarios, alertas, notificaciones, fuentes y canales RSS.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # Los puertos de tu React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"
security = HTTPBearer(auto_error=False)

# ---------------------------------------------------------------------------
# Configuración de email para recuperación de contraseña
# Usa las variables de entorno definidas en el archivo .env
# ---------------------------------------------------------------------------
GMAIL_SENDER = os.getenv("GMAIL_SENDER", "tu_correo@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "xxxx xxxx xxxx xxxx")
FRONTEND_RESET_URL = os.getenv("FRONTEND_RESET_URL")
FRONTEND_VERIFY_URL = os.getenv("FRONTEND_VERIFY_URL")

logger = logging.getLogger("uvicorn.error")
logger.debug("GMAIL_SENDER: %s", GMAIL_SENDER)
logger.debug("GMAIL_APP_PASSWORD: %s", GMAIL_APP_PASSWORD)


print("GMAIL_SENDER:", GMAIL_SENDER, flush=True)
print("GMAIL_APP_PASSWORD:", GMAIL_APP_PASSWORD, flush=True)

def send_verification_email(to_email: str, token: str) -> None:
    """Envía el correo de verificación de cuenta usando Gmail con contraseña de aplicación."""
    verification_link = f"{FRONTEND_RESET_URL}?token={token}"  # Ajusta la URL según tu frontend

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verifica tu cuenta - NewsRadar"
    msg["From"] = GMAIL_SENDER
    msg["To"] = to_email

    text_body = (
        f"Haz clic en el siguiente enlace para verificar tu cuenta:\n"
        f"{verification_link}\n\nEste enlace expira en 24 horas."
    )
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Bienvenido a NewsRadar</h2>
        <p>Gracias por registrarte en <strong>NewsRadar</strong>. Para completar tu registro, verifica tu cuenta haciendo clic en el botón:</p>
        <a href="{verification_link}"
           style="display:inline-block;padding:12px 24px;background:#34a853;color:#fff;text-decoration:none;border-radius:4px;font-weight:bold;">
          Verificar cuenta
        </a>
        <p style="margin-top:24px;color:#666;font-size:13px;">
          Si no realizaste este registro, ignora este correo. El enlace expira en 24 horas.
        </p>
      </body>
    </html>
    """

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_SENDER, to_email, msg.as_string())


def send_reset_password_email(to_email: str, token: str) -> None:
    """Envía el correo de recuperación de contraseña usando Gmail con contraseña de aplicación."""
    reset_link = f"{FRONTEND_RESET_URL}?token={token}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Recuperación de contraseña - NewsRadar"
    msg["From"] = GMAIL_SENDER
    msg["To"] = to_email

    text_body = (
        f"Haz clic en el siguiente enlace para restablecer tu contraseña:\n"
        f"{reset_link}\n\nEste enlace expira en 1 hora."
    )
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Recuperación de contraseña</h2>
        <p>Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en <strong>NewsRadar</strong>.</p>
        <p>Haz clic en el botón para continuar:</p>
        <a href="{reset_link}"
           style="display:inline-block;padding:12px 24px;background:#1a73e8;color:#fff;text-decoration:none;border-radius:4px;font-weight:bold;">
          Restablecer contraseña
        </a>
        <p style="margin-top:24px;color:#666;font-size:13px;">
          Si no solicitaste este cambio, ignora este correo. El enlace expira en 1 hora.
        </p>
      </body>
    </html>
    """

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_SENDER, to_email, msg.as_string())


class Metric(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    value: float


class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class Role(RoleBase):
    id: int


class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=120)
    last_name: str = Field(..., min_length=1, max_length=120)
    organization: str = Field(..., min_length=1, max_length=180)
    role_ids: List[int] = Field(default_factory=list)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=120)
    last_name: Optional[str] = Field(None, min_length=1, max_length=120)
    organization: Optional[str] = Field(None, min_length=1, max_length=180)
    role_ids: Optional[List[int]] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)


class User(UserBase):
    id: int


class UserInDB(User):
    password: str


class AlertCategoryItem(BaseModel):
    code: str = Field(..., min_length=1, max_length=60)
    label: str = Field(..., min_length=1, max_length=120)


class AlertBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    descriptors: List[str] = Field(default_factory=list)
    categories: List[AlertCategoryItem] = Field(default_factory=list)
    cron_expression: str = Field(..., min_length=1, max_length=120)


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    descriptors: Optional[List[str]] = None
    categories: Optional[List[AlertCategoryItem]] = None
    cron_expression: Optional[str] = Field(None, min_length=1, max_length=120)


class SuggestSynonymsRequest(BaseModel):
    """Request para generar sinónimos de palabras clave."""
    keywords: List[str] = Field(..., min_items=1, max_items=5)
    max_synonyms: int = Field(default=5, ge=3, le=10)


class SuggestSynonymsResponse(BaseModel):
    """Response con sugerencias de sinónimos."""
    keywords: List[str]
    suggested_synonyms: List[str]


class Alert(AlertBase):
    id: int
    user_id: int


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    source: str = Field(default="IPTC", pattern="^IPTC$")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    source: Optional[str] = Field(None, pattern="^IPTC$")


class Category(CategoryBase):
    id: int


class NotificationBase(BaseModel):
    timestamp: datetime
    metrics: List[Metric] = Field(default_factory=list)


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    timestamp: Optional[datetime] = None
    metrics: Optional[List[Metric]] = None


class Notification(NotificationBase):
    id: int
    alert_id: int


class InformationSourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    url: HttpUrl


class InformationSourceCreate(InformationSourceBase):
    pass


class InformationSourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    url: Optional[HttpUrl] = None


class InformationSource(InformationSourceBase):
    id: int


class RSSChannelBase(BaseModel):
    url: HttpUrl
    category_id: int


class RSSChannelCreate(RSSChannelBase):
    pass


class RSSChannelUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    category_id: Optional[int] = None


class RSSChannel(RSSChannelBase):
    id: int
    information_source_id: int


class StatsBase(BaseModel):
    metrics: List[Metric] = Field(default_factory=list)


class StatsCreate(StatsBase):
    pass


class StatsUpdate(BaseModel):
    metrics: Optional[List[Metric]] = None


class Stats(StatsBase):
    id: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class VerifyAccountRequest(BaseModel):
    token: str = Field(..., min_length=1)


class VerificationResponse(BaseModel):
    message: str
    success: bool


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=128)

class UserEmailVerificationStatus(BaseModel):
    email: EmailStr
    is_verified: bool

# Token storage (in-memory for simplicity, could be moved to Redis in production)
# password_reset_tokens almacena {token: user_id} — en producción usar Redis con TTL
active_tokens: Dict[str, int] = {}
password_reset_tokens: Dict[str, int] = {}


def sanitize_user(user: UserModel) -> User:
    return User(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        organization=user.organization,
        role_ids=user.role_ids or [],
    )


def user_to_db(user: UserModel) -> UserInDB:
    return UserInDB(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        organization=user.organization,
        role_ids=user.role_ids or [],
        password=user.password,
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> UserInDB:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Token inválido o ausente")

    user_id = active_tokens.get(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario inválido")

    return user_to_db(user)


async def ensure_role_ids_exist(role_ids: List[int], db: AsyncSession) -> None:
    result = await db.execute(select(RoleModel.id).where(RoleModel.id.in_(role_ids)))
    existing_ids = {row[0] for row in result.fetchall()}
    missing = [role_id for role_id in role_ids if role_id not in existing_ids]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Roles no encontrados: {missing}",
        )


async def create_seed_data() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as db:
        # Check if admin user already exists
        result = await db.execute(select(UserModel).where(UserModel.email == "admin@newsradar.com"))
        existing_admin = result.scalar_one_or_none()
        if existing_admin:
            return

        # Create roles
        admin_role = RoleModel(name="admin")
        user_role = RoleModel(name="user")
        db.add(admin_role)
        db.add(user_role)
        await db.flush()

        # Create admin user
        admin_user = UserModel(
            email="admin@newsradar.com",
            first_name="Admin",
            last_name="NewsRadar",
            organization="NewsRadar",
            role_ids=[admin_role.id],
            password="admin123",
            is_verified=True
        )
        db.add(admin_user)
        await db.commit()


@app.on_event("startup")
async def on_startup() -> None:
    await create_seed_data()


@app.get(f"{API_PREFIX}/health", tags=["system"])
def health() -> dict:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post(f"{API_PREFIX}/auth/login", response_model=TokenResponse, tags=["auth"])
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    result = await db.execute(select(UserModel).where(UserModel.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = str(uuid4())
    active_tokens[token] = user.id
    return TokenResponse(access_token=token)


@app.post(f"{API_PREFIX}/auth/register", response_model=User, tags=["auth"])
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    result = await db.execute(select(UserModel).where(UserModel.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    await ensure_role_ids_exist(payload.role_ids, db)

    verification_token = str(uuid4())
    user = UserModel(
        **payload.model_dump(),
        verification_token=verification_token,
        is_verified=False
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    # Enviar email de verificación
    send_verification_email(user.email, verification_token)
    return sanitize_user(user)


@app.post(f"{API_PREFIX}/auth/verify", response_model=VerificationResponse, tags=["auth"])
async def verify_account(
    payload: VerifyAccountRequest,
    db: AsyncSession = Depends(get_db),
) -> VerificationResponse:
    """Verifica la cuenta del usuario usando el token de verificación recibido por email"""
    result = await db.execute(
        select(UserModel).where(UserModel.verification_token == payload.token)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Token de verificación inválido o expirado"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="La cuenta ya ha sido verificada"
        )
    
    user.is_verified = True
    user.verification_token = None
    await db.commit()
    
    return VerificationResponse(
        message="Cuenta verificada exitosamente",
        success=True
    )


@app.post(f"{API_PREFIX}/auth/resend-verification", response_model=VerificationResponse, tags=["auth"])
async def resend_verification(
    payload: EmailStr,
    db: AsyncSession = Depends(get_db),
) -> VerificationResponse:
    """Reenvía el email de verificación a un usuario"""
    result = await db.execute(select(UserModel).where(UserModel.email == payload))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="La cuenta ya está verificada")
    
    # Regenerar token de verificación
    new_verification_token = str(uuid4())
    user.verification_token = new_verification_token
    await db.commit()
    
    # Enviar email con el nuevo token
    send_verification_email(user.email, new_verification_token)
    return VerificationResponse(
        message="Email de verificación reenviado",
        success=True
    )


@app.post(f"{API_PREFIX}/auth/forgot-password", response_model=VerificationResponse, tags=["auth"])
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> VerificationResponse:
    """Solicita el restablecimiento de contraseña. Si el email existe, envía un correo con el enlace."""
    result = await db.execute(select(UserModel).where(UserModel.email == payload.email))
    user = result.scalar_one_or_none()

    # Respuesta genérica para no revelar si el email está registrado
    if not user:
        return VerificationResponse(
            message="Si el correo está registrado, recibirás un enlace para restablecer tu contraseña.",
            success=True,
        )

    # Generar token de recuperación y guardarlo en memoria
    reset_token = str(uuid4())
    password_reset_tokens[reset_token] = user.id

    # TODO: Enviar email con Gmail — descomenta cuando hayas configurado GMAIL_SENDER y GMAIL_APP_PASSWORD
    send_reset_password_email(user.email, reset_token)

    return VerificationResponse(
        message="Si el correo está registrado, recibirás un enlace para restablecer tu contraseña.",
        success=True,
    )


@app.post(f"{API_PREFIX}/auth/reset-password", response_model=VerificationResponse, tags=["auth"])
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> VerificationResponse:
    """Restablece la contraseña usando el token recibido por email."""
    user_id = password_reset_tokens.get(payload.token)
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="Token de recuperación inválido o expirado.",
        )

    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    user.password = payload.new_password
    await db.commit()

    # Invalidar el token una vez usado
    del password_reset_tokens[payload.token]

    return VerificationResponse(
        message="Contraseña restablecida correctamente.",
        success=True,
    )


@app.get(f"{API_PREFIX}/users", response_model=List[User], tags=["users"])
async def list_users(
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[User]:
    result = await db.execute(select(UserModel))
    users = result.scalars().all()
    return [sanitize_user(user) for user in users]


@app.post(f"{API_PREFIX}/users", response_model=User, status_code=201, tags=["users"])
async def create_user(
    payload: UserCreate,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(select(UserModel).where(UserModel.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    await ensure_role_ids_exist(payload.role_ids, db)
    
    user = UserModel(**payload.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return sanitize_user(user)


@app.get(f"{API_PREFIX}/users/{{user_id}}", response_model=User, tags=["users"])
async def get_user(
    user_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return sanitize_user(user)


@app.put(f"{API_PREFIX}/users/{{user_id}}", response_model=User, tags=["users"])
async def update_user(
    user_id: int,
    payload: UserUpdate,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    data = payload.model_dump(exclude_unset=True)
    if "email" in data:
        result = await db.execute(
            select(UserModel).where(UserModel.email == data["email"], UserModel.id != user_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="El email ya está registrado")
    
    if "role_ids" in data:
        await ensure_role_ids_exist(data["role_ids"], db)

    for key, value in data.items():
        setattr(user, key, value)
    
    await db.commit()
    await db.refresh(user)
    return sanitize_user(user)


@app.delete(
    f"{API_PREFIX}/users/{{user_id}}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["users"],
)
async def delete_user(
    user_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
) -> None:
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Get alert IDs to delete notifications from MongoDB
    result = await db.execute(select(AlertModel.id).where(AlertModel.user_id == user_id))
    alert_ids = [row[0] for row in result.fetchall()]
    
    # Delete notifications from MongoDB
    if alert_ids:
        await mongo_db.notifications.delete_many({"alert_id": {"$in": alert_ids}})
    
    # Delete user (cascades to alerts)
    await db.delete(user)
    await db.commit()


@app.get(f"{API_PREFIX}/roles", response_model=List[Role], tags=["roles"])
async def list_roles(
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Role]:
    result = await db.execute(select(RoleModel))
    roles = result.scalars().all()
    return [Role(id=r.id, name=r.name) for r in roles]


@app.post(f"{API_PREFIX}/roles", response_model=Role, status_code=201, tags=["roles"])
async def create_role(
    payload: RoleCreate,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Role:
    role = RoleModel(**payload.model_dump())
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return Role(id=role.id, name=role.name)


@app.get(f"{API_PREFIX}/roles/{{role_id}}", response_model=Role, tags=["roles"])
async def get_role(
    role_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Role:
    result = await db.execute(select(RoleModel).where(RoleModel.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return Role(id=role.id, name=role.name)


@app.put(f"{API_PREFIX}/roles/{{role_id}}", response_model=Role, tags=["roles"])
async def update_role(
    role_id: int,
    payload: RoleUpdate,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Role:
    result = await db.execute(select(RoleModel).where(RoleModel.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(role, key, value)
    
    await db.commit()
    await db.refresh(role)
    return Role(id=role.id, name=role.name)


@app.delete(
    f"{API_PREFIX}/roles/{{role_id}}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["roles"],
)
async def delete_role(
    role_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(RoleModel).where(RoleModel.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    # Check if role is assigned to any user
    result = await db.execute(select(UserModel))
    users = result.scalars().all()
    for user in users:
        if role_id in (user.role_ids or []):
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar un rol asignado a usuarios",
            )

    await db.delete(role)
    await db.commit()


# =========================================================================
# ALERTS & IA ENDPOINTS
# =========================================================================

@app.post(
    f"{API_PREFIX}/alerts/suggest-synonyms",
    response_model=SuggestSynonymsResponse,
    tags=["alerts"],
)
async def suggest_synonyms(
    payload: SuggestSynonymsRequest,
    _: UserInDB = Depends(get_current_user),
) -> SuggestSynonymsResponse:
    """
    Sugiere sinónimos y palabras relacionadas para palabras clave.
    
    Utiliza IA (OpenAI gpt-3.5-turbo) para generar sinónimos que amplíen
    la cobertura de búsqueda de noticias.
    
    RF-02: Sugerencia automática de sinónimos durante la creación de alertas
    """
    suggested = generate_synonyms(payload.keywords, payload.max_synonyms)
    
    return SuggestSynonymsResponse(
        keywords=payload.keywords,
        suggested_synonyms=suggested,
    )


@app.get(
    f"{API_PREFIX}/users/{{user_id}}/alerts",
    response_model=List[Alert],
    tags=["alerts"],
)
async def list_user_alerts(
    user_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Alert]:
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    result = await db.execute(select(AlertModel).where(AlertModel.user_id == user_id))
    alerts = result.scalars().all()
    return [
        Alert(
            id=a.id,
            user_id=a.user_id,
            name=a.name,
            descriptors=a.descriptors or [],
            categories=[AlertCategoryItem(**c) for c in (a.categories or [])],
            cron_expression=a.cron_expression,
        )
        for a in alerts
    ]


@app.post(
    f"{API_PREFIX}/users/{{user_id}}/alerts",
    response_model=Alert,
    status_code=201,
    tags=["alerts"],
)
async def create_user_alert(
    user_id: int,
    payload: AlertCreate,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Alert:
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    alert_data = payload.model_dump()
    alert_data["categories"] = [c.model_dump() for c in payload.categories]
    alert = AlertModel(user_id=user_id, **alert_data)
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    
    return Alert(
        id=alert.id,
        user_id=alert.user_id,
        name=alert.name,
        descriptors=alert.descriptors or [],
        categories=[AlertCategoryItem(**c) for c in (alert.categories or [])],
        cron_expression=alert.cron_expression,
    )


@app.get(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}",
    response_model=Alert,
    tags=["alerts"],
)
async def get_user_alert(
    user_id: int,
    alert_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Alert:
    result = await db.execute(
        select(AlertModel).where(AlertModel.id == alert_id, AlertModel.user_id == user_id)
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    
    return Alert(
        id=alert.id,
        user_id=alert.user_id,
        name=alert.name,
        descriptors=alert.descriptors or [],
        categories=[AlertCategoryItem(**c) for c in (alert.categories or [])],
        cron_expression=alert.cron_expression,
    )


@app.put(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}",
    response_model=Alert,
    tags=["alerts"],
)
async def update_user_alert(
    user_id: int,
    alert_id: int,
    payload: AlertUpdate,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Alert:
    result = await db.execute(
        select(AlertModel).where(AlertModel.id == alert_id, AlertModel.user_id == user_id)
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    
    data = payload.model_dump(exclude_unset=True)
    if "categories" in data and data["categories"] is not None:
        data["categories"] = [c.model_dump() for c in payload.categories]
    
    for key, value in data.items():
        setattr(alert, key, value)
    
    await db.commit()
    await db.refresh(alert)
    
    return Alert(
        id=alert.id,
        user_id=alert.user_id,
        name=alert.name,
        descriptors=alert.descriptors or [],
        categories=[AlertCategoryItem(**c) for c in (alert.categories or [])],
        cron_expression=alert.cron_expression,
    )


@app.delete(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["alerts"],
)
async def delete_user_alert(
    user_id: int,
    alert_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
) -> None:
    result = await db.execute(
        select(AlertModel).where(AlertModel.id == alert_id, AlertModel.user_id == user_id)
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    
    # Delete notifications from MongoDB
    await mongo_db.notifications.delete_many({"alert_id": alert_id})
    
    await db.delete(alert)
    await db.commit()


@app.get(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications",
    response_model=List[Notification],
    tags=["notifications"],
)
async def list_alert_notifications(
    user_id: int,
    alert_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
) -> List[Notification]:
    result = await db.execute(
        select(AlertModel).where(AlertModel.id == alert_id, AlertModel.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    
    cursor = mongo_db.notifications.find({"alert_id": alert_id})
    notifications = await cursor.to_list(length=None)
    
    return [
        Notification(
            id=n["_id"],
            alert_id=n["alert_id"],
            timestamp=n["timestamp"],
            metrics=[Metric(**m) for m in n.get("metrics", [])],
        )
        for n in notifications
    ]


@app.post(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications",
    response_model=Notification,
    status_code=201,
    tags=["notifications"],
)
async def create_alert_notification(
    user_id: int,
    alert_id: int,
    payload: NotificationCreate,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
) -> Notification:
    result = await db.execute(
        select(AlertModel).where(AlertModel.id == alert_id, AlertModel.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    
    # Get next ID
    last_doc = await mongo_db.notifications.find_one(sort=[("_id", -1)])
    next_id = (last_doc["_id"] + 1) if last_doc else 1
    
    doc = {
        "_id": next_id,
        "alert_id": alert_id,
        "timestamp": payload.timestamp,
        "metrics": [m.model_dump() for m in payload.metrics],
    }
    await mongo_db.notifications.insert_one(doc)
    
    return Notification(
        id=next_id,
        alert_id=alert_id,
        timestamp=payload.timestamp,
        metrics=payload.metrics,
    )


@app.get(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications/{{notification_id}}",
    response_model=Notification,
    tags=["notifications"],
)
async def get_alert_notification(
    user_id: int,
    alert_id: int,
    notification_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
) -> Notification:
    result = await db.execute(
        select(AlertModel).where(AlertModel.id == alert_id, AlertModel.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    
    doc = await mongo_db.notifications.find_one({"_id": notification_id, "alert_id": alert_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Notificación no encontrada para la alerta")
    
    return Notification(
        id=doc["_id"],
        alert_id=doc["alert_id"],
        timestamp=doc["timestamp"],
        metrics=[Metric(**m) for m in doc.get("metrics", [])],
    )


@app.put(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications/{{notification_id}}",
    response_model=Notification,
    tags=["notifications"],
)
async def update_alert_notification(
    user_id: int,
    alert_id: int,
    notification_id: int,
    payload: NotificationUpdate,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
) -> Notification:
    result = await db.execute(
        select(AlertModel).where(AlertModel.id == alert_id, AlertModel.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    
    doc = await mongo_db.notifications.find_one({"_id": notification_id, "alert_id": alert_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Notificación no encontrada para la alerta")
    
    update_data = {}
    if payload.timestamp is not None:
        update_data["timestamp"] = payload.timestamp
    if payload.metrics is not None:
        update_data["metrics"] = [m.model_dump() for m in payload.metrics]
    
    if update_data:
        await mongo_db.notifications.update_one(
            {"_id": notification_id},
            {"$set": update_data}
        )
        doc.update(update_data)
    
    return Notification(
        id=doc["_id"],
        alert_id=doc["alert_id"],
        timestamp=doc["timestamp"],
        metrics=[Metric(**m) for m in doc.get("metrics", [])],
    )


@app.delete(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications/{{notification_id}}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["notifications"],
)
async def delete_alert_notification(
    user_id: int,
    alert_id: int,
    notification_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
) -> None:
    result = await db.execute(
        select(AlertModel).where(AlertModel.id == alert_id, AlertModel.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    
    result = await mongo_db.notifications.delete_one({"_id": notification_id, "alert_id": alert_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notificación no encontrada para la alerta")


@app.get(f"{API_PREFIX}/categories", response_model=List[Category], tags=["categories"])
async def list_categories(
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Category]:
    result = await db.execute(select(CategoryModel))
    categories = result.scalars().all()
    return [Category(id=c.id, name=c.name, source=c.source) for c in categories]


@app.post(f"{API_PREFIX}/categories", response_model=Category, status_code=201, tags=["categories"])
async def create_category(
    payload: CategoryCreate,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Category:
    category = CategoryModel(**payload.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return Category(id=category.id, name=category.name, source=category.source)


@app.get(f"{API_PREFIX}/categories/{{category_id}}", response_model=Category, tags=["categories"])
async def get_category(
    category_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Category:
    result = await db.execute(select(CategoryModel).where(CategoryModel.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return Category(id=category.id, name=category.name, source=category.source)


@app.put(f"{API_PREFIX}/categories/{{category_id}}", response_model=Category, tags=["categories"])
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Category:
    result = await db.execute(select(CategoryModel).where(CategoryModel.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(category, key, value)
    
    await db.commit()
    await db.refresh(category)
    return Category(id=category.id, name=category.name, source=category.source)


@app.delete(
    f"{API_PREFIX}/categories/{{category_id}}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["categories"],
)
async def delete_category(
    category_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(CategoryModel).where(CategoryModel.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    # Check if category is used by any RSS channel
    result = await db.execute(select(RSSChannelModel).where(RSSChannelModel.category_id == category_id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Categoría asociada a canales RSS")

    await db.delete(category)
    await db.commit()


@app.get(
    f"{API_PREFIX}/information-sources",
    response_model=List[InformationSource],
    tags=["information-sources"],
)
async def list_information_sources(
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[InformationSource]:
    result = await db.execute(select(InformationSourceModel))
    sources = result.scalars().all()
    return [InformationSource(id=s.id, name=s.name, url=s.url) for s in sources]


@app.post(
    f"{API_PREFIX}/information-sources",
    response_model=InformationSource,
    status_code=201,
    tags=["information-sources"],
)
async def create_information_source(
    payload: InformationSourceCreate,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InformationSource:
    source = InformationSourceModel(**payload.model_dump())
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return InformationSource(id=source.id, name=source.name, url=source.url)


@app.get(
    f"{API_PREFIX}/information-sources/{{source_id}}",
    response_model=InformationSource,
    tags=["information-sources"],
)
async def get_information_source(
    source_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InformationSource:
    result = await db.execute(select(InformationSourceModel).where(InformationSourceModel.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    return InformationSource(id=source.id, name=source.name, url=source.url)


@app.put(
    f"{API_PREFIX}/information-sources/{{source_id}}",
    response_model=InformationSource,
    tags=["information-sources"],
)
async def update_information_source(
    source_id: int,
    payload: InformationSourceUpdate,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InformationSource:
    result = await db.execute(select(InformationSourceModel).where(InformationSourceModel.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(source, key, value)
    
    await db.commit()
    await db.refresh(source)
    return InformationSource(id=source.id, name=source.name, url=source.url)


@app.delete(
    f"{API_PREFIX}/information-sources/{{source_id}}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["information-sources"],
)
async def delete_information_source(
    source_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(InformationSourceModel).where(InformationSourceModel.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")

    # Delete will cascade to RSS channels
    await db.delete(source)
    await db.commit()


@app.get(
    f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels",
    response_model=List[RSSChannel],
    tags=["rss-channels"],
)
async def list_source_channels(
    source_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[RSSChannel]:
    result = await db.execute(select(InformationSourceModel).where(InformationSourceModel.id == source_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    
    result = await db.execute(
        select(RSSChannelModel).where(RSSChannelModel.information_source_id == source_id)
    )
    channels = result.scalars().all()
    return [
        RSSChannel(
            id=c.id,
            information_source_id=c.information_source_id,
            url=c.url,
            category_id=c.category_id,
        )
        for c in channels
    ]


@app.post(
    f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels",
    response_model=RSSChannel,
    status_code=201,
    tags=["rss-channels"],
)
async def create_source_channel(
    source_id: int,
    payload: RSSChannelCreate,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RSSChannel:
    result = await db.execute(select(InformationSourceModel).where(InformationSourceModel.id == source_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    
    result = await db.execute(select(CategoryModel).where(CategoryModel.id == payload.category_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    channel = RSSChannelModel(
        information_source_id=source_id,
        **payload.model_dump(),
    )
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    
    return RSSChannel(
        id=channel.id,
        information_source_id=channel.information_source_id,
        url=channel.url,
        category_id=channel.category_id,
    )


@app.get(
    f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels/{{channel_id}}",
    response_model=RSSChannel,
    tags=["rss-channels"],
)
async def get_source_channel(
    source_id: int,
    channel_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RSSChannel:
    result = await db.execute(select(InformationSourceModel).where(InformationSourceModel.id == source_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    
    result = await db.execute(
        select(RSSChannelModel).where(
            RSSChannelModel.id == channel_id,
            RSSChannelModel.information_source_id == source_id,
        )
    )
    channel = result.scalar_one_or_none()
    if not channel:
        raise HTTPException(status_code=404, detail="Canal RSS no encontrado para la fuente")
    
    return RSSChannel(
        id=channel.id,
        information_source_id=channel.information_source_id,
        url=channel.url,
        category_id=channel.category_id,
    )


@app.put(
    f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels/{{channel_id}}",
    response_model=RSSChannel,
    tags=["rss-channels"],
)
async def update_source_channel(
    source_id: int,
    channel_id: int,
    payload: RSSChannelUpdate,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RSSChannel:
    result = await db.execute(select(InformationSourceModel).where(InformationSourceModel.id == source_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    
    result = await db.execute(
        select(RSSChannelModel).where(
            RSSChannelModel.id == channel_id,
            RSSChannelModel.information_source_id == source_id,
        )
    )
    channel = result.scalar_one_or_none()
    if not channel:
        raise HTTPException(status_code=404, detail="Canal RSS no encontrado para la fuente")

    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data:
        result = await db.execute(select(CategoryModel).where(CategoryModel.id == data["category_id"]))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

    for key, value in data.items():
        setattr(channel, key, value)
    
    await db.commit()
    await db.refresh(channel)
    
    return RSSChannel(
        id=channel.id,
        information_source_id=channel.information_source_id,
        url=channel.url,
        category_id=channel.category_id,
    )


@app.delete(
    f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels/{{channel_id}}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["rss-channels"],
)
async def delete_source_channel(
    source_id: int,
    channel_id: int,
    _: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(InformationSourceModel).where(InformationSourceModel.id == source_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    
    result = await db.execute(
        select(RSSChannelModel).where(
            RSSChannelModel.id == channel_id,
            RSSChannelModel.information_source_id == source_id,
        )
    )
    channel = result.scalar_one_or_none()
    if not channel:
        raise HTTPException(status_code=404, detail="Canal RSS no encontrado para la fuente")
    
    await db.delete(channel)
    await db.commit()


@app.get(f"{API_PREFIX}/stats", response_model=List[Stats], tags=["stats"])
async def list_stats(
    _: UserInDB = Depends(get_current_user),
    mongo_db=Depends(get_mongo_db),
) -> List[Stats]:
    cursor = mongo_db.stats.find()
    stats_list = await cursor.to_list(length=None)
    return [
        Stats(
            id=s["_id"],
            metrics=[Metric(**m) for m in s.get("metrics", [])],
        )
        for s in stats_list
    ]


@app.post(f"{API_PREFIX}/stats", response_model=Stats, status_code=201, tags=["stats"])
async def create_stats(
    payload: StatsCreate,
    _: UserInDB = Depends(get_current_user),
    mongo_db=Depends(get_mongo_db),
) -> Stats:
    # Get next ID
    last_doc = await mongo_db.stats.find_one(sort=[("_id", -1)])
    next_id = (last_doc["_id"] + 1) if last_doc else 1
    
    doc = {
        "_id": next_id,
        "metrics": [m.model_dump() for m in payload.metrics],
    }
    await mongo_db.stats.insert_one(doc)
    
    return Stats(id=next_id, metrics=payload.metrics)


@app.get(f"{API_PREFIX}/stats/{{stats_id}}", response_model=Stats, tags=["stats"])
async def get_stats(
    stats_id: int,
    _: UserInDB = Depends(get_current_user),
    mongo_db=Depends(get_mongo_db),
) -> Stats:
    doc = await mongo_db.stats.find_one({"_id": stats_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Stats no encontrados")
    
    return Stats(
        id=doc["_id"],
        metrics=[Metric(**m) for m in doc.get("metrics", [])],
    )


@app.put(f"{API_PREFIX}/stats/{{stats_id}}", response_model=Stats, tags=["stats"])
async def update_stats(
    stats_id: int,
    payload: StatsUpdate,
    _: UserInDB = Depends(get_current_user),
    mongo_db=Depends(get_mongo_db),
) -> Stats:
    doc = await mongo_db.stats.find_one({"_id": stats_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Stats no encontrados")

    update_data = {}
    if payload.metrics is not None:
        update_data["metrics"] = [m.model_dump() for m in payload.metrics]
    
    if update_data:
        await mongo_db.stats.update_one(
            {"_id": stats_id},
            {"$set": update_data}
        )
        doc.update(update_data)
    
    return Stats(
        id=doc["_id"],
        metrics=[Metric(**m) for m in doc.get("metrics", [])],
    )


@app.delete(
    f"{API_PREFIX}/stats/{{stats_id}}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["stats"],
)
async def delete_stats(
    stats_id: int,
    _: UserInDB = Depends(get_current_user),
    mongo_db=Depends(get_mongo_db),
) -> None:
    result = await mongo_db.stats.delete_one({"_id": stats_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Stats no encontrados")
    
@app.get(
    f"{API_PREFIX}/users/email/{{email}}/verification-status", 
    response_model=UserEmailVerificationStatus, 
    tags=["users"]
)
async def get_user_verification_status_by_email(
    email: EmailStr,
    _: UserInDB = Depends(get_current_user), # Borra esta línea si quieres que el endpoint sea público
    db: AsyncSession = Depends(get_db),
) -> UserEmailVerificationStatus:
    """Comprueba si la cuenta de un usuario está verificada a partir de su correo electrónico."""
    
    # Hacemos la consulta a la base de datos buscando por email
    result = await db.execute(select(UserModel).where(UserModel.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    # Devolvemos el email y el valor de la columna is_verified (que será True/False equivalente a t/f en Postgres)
    return UserEmailVerificationStatus(
        email=user.email, 
        is_verified=user.is_verified
    )