from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from bson import ObjectId

import jwt
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, engine, AsyncSessionLocal
from database_mongodb import get_mongo_db
from motor.motor_asyncio import AsyncIOMotorDatabase

# ─── Modelos SQLAlchemy (ORM) ────────────────────────────────────────────────
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, String, JSON, ForeignKey

class Base(DeclarativeBase):
    pass

class RoleORM(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(120))
    last_name = Column(String(120))
    organization = Column(String(180))
    password = Column(String(128))
    role_ids = Column(JSON, default=list)
    alerts = relationship("AlertORM", back_populates="user", cascade="all, delete-orphan")

class AlertORM(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    descriptors = Column(JSON, default=list)
    categories = Column(JSON, default=list)
    cron_expression = Column(String(120))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserORM", back_populates="alerts")

class CategoryORM(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    source = Column(String(10), default="IPTC")

class InformationSourceORM(Base):
    __tablename__ = "information_sources"
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    url = Column(String(500))
    channels = relationship("RSSChannelORM", back_populates="source", cascade="all, delete-orphan")

class RSSChannelORM(Base):
    __tablename__ = "rss_channels"
    id = Column(Integer, primary_key=True)
    url = Column(String(500))
    category_id = Column(Integer, ForeignKey("categories.id"))
    information_source_id = Column(Integer, ForeignKey("information_sources.id"))
    source = relationship("InformationSourceORM", back_populates="channels")


# ─── Configuración JWT ───────────────────────────────────────────────────────
SECRET_KEY = "clave-provisional"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(
    title="NewsRadar API",
    version="1.0.0",
    description="API REST para gestión de usuarios, alertas, notificaciones, fuentes y canales RSS.",
)

API_PREFIX = "/api/v1"
security = HTTPBearer(auto_error=False)


# ─── Schemas Pydantic ────────────────────────────────────────────────────────
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
    class Config:
        from_attributes = True

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
    class Config:
        from_attributes = True

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

class Alert(AlertBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

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
    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    timestamp: datetime
    metrics: List[Metric] = Field(default_factory=list)

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    timestamp: Optional[datetime] = None
    metrics: Optional[List[Metric]] = None

class Notification(NotificationBase):
    id: str
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
    class Config:
        from_attributes = True

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
    class Config:
        from_attributes = True

class StatsBase(BaseModel):
    metrics: List[Metric] = Field(default_factory=list)

class StatsCreate(StatsBase):
    pass

class StatsUpdate(BaseModel):
    metrics: Optional[List[Metric]] = None

class Stats(StatsBase):
    id: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── Helpers de autenticación ────────────────────────────────────────────────
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> UserORM:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Token inválido o ausente")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        user_id = int(user_id_str)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = await db.get(UserORM, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado en base de datos")
    return user


async def require_admin(user: UserORM = Depends(get_current_user)) -> UserORM:
    if 1 not in (user.role_ids or []):
        raise HTTPException(status_code=403, detail="Acceso denegado: Se requiere rol de Gestor")
    return user


# ─── Startup ─────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup() -> None:
    # Crear tablas en PostgreSQL
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed data si no hay roles
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(RoleORM))
        if not result.scalars().first():
            admin_role = RoleORM(name="admin")
            user_role = RoleORM(name="user")
            db.add_all([admin_role, user_role])
            await db.flush()

            db.add(UserORM(
                email="admin@newsradar.com",
                first_name="Admin",
                last_name="NewsRadar",
                organization="NewsRadar",
                role_ids=[admin_role.id],
                password="admin123",
            ))
            db.add(UserORM(
                email="lector@newsradar.com",
                first_name="Lector",
                last_name="NewsRadar",
                organization="NewsRadar",
                role_ids=[user_role.id],
                password="lector123",
            ))
            await db.commit()


# ─── Health ───────────────────────────────────────────────────────────────────
@app.get(f"{API_PREFIX}/health", tags=["system"])
def health() -> dict:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


# ─── Auth ─────────────────────────────────────────────────────────────────────
@app.post(f"{API_PREFIX}/auth/login", response_model=TokenResponse, tags=["auth"])
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    result = await db.execute(select(UserORM).where(UserORM.email == payload.email))
    user = result.scalars().first()
    if not user or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {"sub": str(user.id), "exp": expire, "roles": user.role_ids}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return TokenResponse(access_token=token)


@app.post(f"{API_PREFIX}/auth/register", response_model=User, tags=["auth"])
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    existing = await db.execute(select(UserORM).where(UserORM.email == payload.email))
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    # Validar que los roles existen
    for role_id in payload.role_ids:
        role = await db.get(RoleORM, role_id)
        if not role:
            raise HTTPException(status_code=400, detail=f"Rol no encontrado: {role_id}")

    user = UserORM(**payload.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ─── Roles ────────────────────────────────────────────────────────────────────
@app.get(f"{API_PREFIX}/roles", response_model=List[Role], tags=["roles"])
async def list_roles(_: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RoleORM))
    return result.scalars().all()


@app.post(f"{API_PREFIX}/roles", response_model=Role, status_code=201, tags=["roles"])
async def create_role(payload: RoleCreate, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    role = RoleORM(**payload.model_dump())
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@app.get(f"{API_PREFIX}/roles/{{role_id}}", response_model=Role, tags=["roles"])
async def get_role(role_id: int, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    role = await db.get(RoleORM, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return role


@app.put(f"{API_PREFIX}/roles/{{role_id}}", response_model=Role, tags=["roles"])
async def update_role(role_id: int, payload: RoleUpdate, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    role = await db.get(RoleORM, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    for key, val in payload.model_dump(exclude_unset=True).items():
        setattr(role, key, val)
    await db.commit()
    await db.refresh(role)
    return role


@app.delete(f"{API_PREFIX}/roles/{{role_id}}", status_code=204, response_model=None, response_class=Response, tags=["roles"])
async def delete_role(role_id: int, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    role = await db.get(RoleORM, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    # No eliminar si hay usuarios con este rol
    result = await db.execute(select(UserORM))
    users = result.scalars().all()
    for user in users:
        if role_id in (user.role_ids or []):
            raise HTTPException(status_code=409, detail="No se puede eliminar un rol asignado a usuarios")

    await db.delete(role)
    await db.commit()


# ─── Users ────────────────────────────────────────────────────────────────────
@app.get(f"{API_PREFIX}/users", response_model=List[User], tags=["users"])
async def list_users(_: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserORM))
    return result.scalars().all()


@app.post(f"{API_PREFIX}/users", response_model=User, status_code=201, tags=["users"])
async def create_user(payload: UserCreate, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(UserORM).where(UserORM.email == payload.email))
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    for role_id in payload.role_ids:
        if not await db.get(RoleORM, role_id):
            raise HTTPException(status_code=400, detail=f"Rol no encontrado: {role_id}")

    user = UserORM(**payload.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@app.get(f"{API_PREFIX}/users/{{user_id}}", response_model=User, tags=["users"])
async def get_user(user_id: int, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await db.get(UserORM, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@app.put(f"{API_PREFIX}/users/{{user_id}}", response_model=User, tags=["users"])
async def update_user(user_id: int, payload: UserUpdate, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await db.get(UserORM, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    data = payload.model_dump(exclude_unset=True)

    if "email" in data:
        dup = await db.execute(select(UserORM).where(UserORM.email == data["email"], UserORM.id != user_id))
        if dup.scalars().first():
            raise HTTPException(status_code=409, detail="El email ya está registrado")

    if "role_ids" in data:
        for role_id in data["role_ids"]:
            if not await db.get(RoleORM, role_id):
                raise HTTPException(status_code=400, detail=f"Rol no encontrado: {role_id}")

    for key, val in data.items():
        setattr(user, key, val)
    await db.commit()
    await db.refresh(user)
    return user


@app.delete(f"{API_PREFIX}/users/{{user_id}}", status_code=204, response_model=None, response_class=Response, tags=["users"])
async def delete_user(user_id: int, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await db.get(UserORM, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    await db.delete(user)  # cascade elimina sus alertas
    await db.commit()


# ─── Alerts ───────────────────────────────────────────────────────────────────
@app.get(f"{API_PREFIX}/users/{{user_id}}/alerts", response_model=List[Alert], tags=["alerts"])
async def list_user_alerts(user_id: int, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not await db.get(UserORM, user_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    result = await db.execute(select(AlertORM).where(AlertORM.user_id == user_id))
    return result.scalars().all()


@app.post(f"{API_PREFIX}/users/{{user_id}}/alerts", response_model=Alert, status_code=201, tags=["alerts"])
async def create_user_alert(user_id: int, payload: AlertCreate, _: UserORM = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    if not await db.get(UserORM, user_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    alert = AlertORM(user_id=user_id, **payload.model_dump())
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


@app.get(f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}", response_model=Alert, tags=["alerts"])
async def get_user_alert(user_id: int, alert_id: int, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    alert = await db.get(AlertORM, alert_id)
    if not alert or alert.user_id != user_id:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    return alert


@app.put(f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}", response_model=Alert, tags=["alerts"])
async def update_user_alert(user_id: int, alert_id: int, payload: AlertUpdate, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    alert = await db.get(AlertORM, alert_id)
    if not alert or alert.user_id != user_id:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    for key, val in payload.model_dump(exclude_unset=True).items():
        setattr(alert, key, val)
    await db.commit()
    await db.refresh(alert)
    return alert


@app.delete(f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}", status_code=204, response_model=None, response_class=Response, tags=["alerts"])
async def delete_user_alert(user_id: int, alert_id: int, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    alert = await db.get(AlertORM, alert_id)
    if not alert or alert.user_id != user_id:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    # Eliminar notificaciones de MongoDB asociadas
    await mongo.notifications.delete_many({"alert_id": alert_id})
    await db.delete(alert)
    await db.commit()


# ─── Notifications (MongoDB) ──────────────────────────────────────────────────
def _serialize_notification(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


@app.get(f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications", response_model=List[Notification], tags=["notifications"])
async def list_alert_notifications(user_id: int, alert_id: int, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    alert = await db.get(AlertORM, alert_id)
    if not alert or alert.user_id != user_id:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    cursor = mongo.notifications.find({"alert_id": alert_id})
    docs = await cursor.to_list(length=None)
    return [_serialize_notification(d) for d in docs]


@app.post(f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications", response_model=Notification, status_code=201, tags=["notifications"])
async def create_alert_notification(user_id: int, alert_id: int, payload: NotificationCreate, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    alert = await db.get(AlertORM, alert_id)
    if not alert or alert.user_id != user_id:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    doc = {"alert_id": alert_id, **payload.model_dump()}
    result = await mongo.notifications.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    return doc


@app.get(f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications/{{notification_id}}", response_model=Notification, tags=["notifications"])
async def get_alert_notification(user_id: int, alert_id: int, notification_id: str, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    alert = await db.get(AlertORM, alert_id)
    if not alert or alert.user_id != user_id:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    doc = await mongo.notifications.find_one({"_id": ObjectId(notification_id), "alert_id": alert_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return _serialize_notification(doc)


@app.put(f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications/{{notification_id}}", response_model=Notification, tags=["notifications"])
async def update_alert_notification(user_id: int, alert_id: int, notification_id: str, payload: NotificationUpdate, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    alert = await db.get(AlertORM, alert_id)
    if not alert or alert.user_id != user_id:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    update_data = payload.model_dump(exclude_unset=True)
    await mongo.notifications.update_one({"_id": ObjectId(notification_id)}, {"$set": update_data})
    doc = await mongo.notifications.find_one({"_id": ObjectId(notification_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return _serialize_notification(doc)


@app.delete(f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications/{{notification_id}}", status_code=204, response_model=None, response_class=Response, tags=["notifications"])
async def delete_alert_notification(user_id: int, alert_id: int, notification_id: str, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    alert = await db.get(AlertORM, alert_id)
    if not alert or alert.user_id != user_id:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    await mongo.notifications.delete_one({"_id": ObjectId(notification_id), "alert_id": alert_id})


# ─── Categories ───────────────────────────────────────────────────────────────
@app.get(f"{API_PREFIX}/categories", response_model=List[Category], tags=["categories"])
async def list_categories(_: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CategoryORM))
    return result.scalars().all()


@app.post(f"{API_PREFIX}/categories", response_model=Category, status_code=201, tags=["categories"])
async def create_category(payload: CategoryCreate, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    category = CategoryORM(**payload.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@app.get(f"{API_PREFIX}/categories/{{category_id}}", response_model=Category, tags=["categories"])
async def get_category(category_id: int, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    category = await db.get(CategoryORM, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category


@app.put(f"{API_PREFIX}/categories/{{category_id}}", response_model=Category, tags=["categories"])
async def update_category(category_id: int, payload: CategoryUpdate, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    category = await db.get(CategoryORM, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    for key, val in payload.model_dump(exclude_unset=True).items():
        setattr(category, key, val)
    await db.commit()
    await db.refresh(category)
    return category


@app.delete(f"{API_PREFIX}/categories/{{category_id}}", status_code=204, response_model=None, response_class=Response, tags=["categories"])
async def delete_category(category_id: int, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    category = await db.get(CategoryORM, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    # Verificar si hay canales RSS usando esta categoría
    result = await db.execute(select(RSSChannelORM).where(RSSChannelORM.category_id == category_id))
    if result.scalars().first():
        raise HTTPException(status_code=409, detail="Categoría asociada a canales RSS")
    await db.delete(category)
    await db.commit()


# ─── Information Sources ──────────────────────────────────────────────────────
@app.get(f"{API_PREFIX}/information-sources", response_model=List[InformationSource], tags=["information-sources"])
async def list_information_sources(_: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InformationSourceORM))
    return result.scalars().all()


@app.post(f"{API_PREFIX}/information-sources", response_model=InformationSource, status_code=201, tags=["information-sources"])
async def create_information_source(payload: InformationSourceCreate, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    source = InformationSourceORM(name=payload.name, url=str(payload.url))
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@app.get(f"{API_PREFIX}/information-sources/{{source_id}}", response_model=InformationSource, tags=["information-sources"])
async def get_information_source(source_id: int, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    source = await db.get(InformationSourceORM, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    return source


@app.put(f"{API_PREFIX}/information-sources/{{source_id}}", response_model=InformationSource, tags=["information-sources"])
async def update_information_source(source_id: int, payload: InformationSourceUpdate, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    source = await db.get(InformationSourceORM, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    data = payload.model_dump(exclude_unset=True)
    if "url" in data:
        data["url"] = str(data["url"])
    for key, val in data.items():
        setattr(source, key, val)
    await db.commit()
    await db.refresh(source)
    return source


@app.delete(f"{API_PREFIX}/information-sources/{{source_id}}", status_code=204, response_model=None, response_class=Response, tags=["information-sources"])
async def delete_information_source(source_id: int, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    source = await db.get(InformationSourceORM, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    await db.delete(source)  # cascade elimina sus canales RSS
    await db.commit()


# ─── RSS Channels ─────────────────────────────────────────────────────────────
@app.get(f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels", response_model=List[RSSChannel], tags=["rss-channels"])
async def list_source_channels(source_id: int, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not await db.get(InformationSourceORM, source_id):
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    result = await db.execute(select(RSSChannelORM).where(RSSChannelORM.information_source_id == source_id))
    return result.scalars().all()


@app.post(f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels", response_model=RSSChannel, status_code=201, tags=["rss-channels"])
async def create_source_channel(source_id: int, payload: RSSChannelCreate, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not await db.get(InformationSourceORM, source_id):
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    if not await db.get(CategoryORM, payload.category_id):
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    channel = RSSChannelORM(information_source_id=source_id, url=str(payload.url), category_id=payload.category_id)
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    return channel


@app.get(f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels/{{channel_id}}", response_model=RSSChannel, tags=["rss-channels"])
async def get_source_channel(source_id: int, channel_id: int, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not await db.get(InformationSourceORM, source_id):
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    channel = await db.get(RSSChannelORM, channel_id)
    if not channel or channel.information_source_id != source_id:
        raise HTTPException(status_code=404, detail="Canal RSS no encontrado para la fuente")
    return channel


@app.put(f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels/{{channel_id}}", response_model=RSSChannel, tags=["rss-channels"])
async def update_source_channel(source_id: int, channel_id: int, payload: RSSChannelUpdate, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not await db.get(InformationSourceORM, source_id):
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    channel = await db.get(RSSChannelORM, channel_id)
    if not channel or channel.information_source_id != source_id:
        raise HTTPException(status_code=404, detail="Canal RSS no encontrado para la fuente")
    data = payload.model_dump(exclude_unset=True)
    if "url" in data:
        data["url"] = str(data["url"])
    if "category_id" in data and not await db.get(CategoryORM, data["category_id"]):
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    for key, val in data.items():
        setattr(channel, key, val)
    await db.commit()
    await db.refresh(channel)
    return channel


@app.delete(f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels/{{channel_id}}", status_code=204, response_model=None, response_class=Response, tags=["rss-channels"])
async def delete_source_channel(source_id: int, channel_id: int, _: UserORM = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not await db.get(InformationSourceORM, source_id):
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    channel = await db.get(RSSChannelORM, channel_id)
    if not channel or channel.information_source_id != source_id:
        raise HTTPException(status_code=404, detail="Canal RSS no encontrado para la fuente")
    await db.delete(channel)
    await db.commit()


# ─── Stats (MongoDB) ──────────────────────────────────────────────────────────
def _serialize_stats(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


@app.get(f"{API_PREFIX}/stats", response_model=List[Stats], tags=["stats"])
async def list_stats(_: UserORM = Depends(get_current_user), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    docs = await mongo.stats.find().to_list(length=None)
    return [_serialize_stats(d) for d in docs]


@app.post(f"{API_PREFIX}/stats", response_model=Stats, status_code=201, tags=["stats"])
async def create_stats(payload: StatsCreate, _: UserORM = Depends(get_current_user), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    doc = payload.model_dump()
    result = await mongo.stats.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    return doc


@app.get(f"{API_PREFIX}/stats/{{stats_id}}", response_model=Stats, tags=["stats"])
async def get_stats(stats_id: str, _: UserORM = Depends(get_current_user), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    doc = await mongo.stats.find_one({"_id": ObjectId(stats_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Stats no encontrados")
    return _serialize_stats(doc)


@app.put(f"{API_PREFIX}/stats/{{stats_id}}", response_model=Stats, tags=["stats"])
async def update_stats(stats_id: str, payload: StatsUpdate, _: UserORM = Depends(get_current_user), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    update_data = payload.model_dump(exclude_unset=True)
    await mongo.stats.update_one({"_id": ObjectId(stats_id)}, {"$set": update_data})
    doc = await mongo.stats.find_one({"_id": ObjectId(stats_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Stats no encontrados")
    return _serialize_stats(doc)


@app.delete(f"{API_PREFIX}/stats/{{stats_id}}", status_code=204, response_model=None, response_class=Response, tags=["stats"])
async def delete_stats(stats_id: str, _: UserORM = Depends(get_current_user), mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    result = await mongo.stats.delete_one({"_id": ObjectId(stats_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Stats no encontrados")