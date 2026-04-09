# main.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, Base, engine  # Asegúrate de que database.py esté en el path
from database_mongodb import get_mongo_db
from models import Role as RoleModel, User as UserModel, Alert as AlertModel
from models import Category as CategoryModel, InformationSource as InformationSourceModel, RSSChannel as RSSChannelModel

app = FastAPI(
    title="NewsRadar API",
    version="1.0.0",
    description="API REST para gestión de usuarios, alertas, notificaciones, fuentes y canales RSS.",
)

API_PREFIX = "/api/v1"
security = HTTPBearer(auto_error=False)

# ------------------------------------------------------------
# Modelos Pydantic (exactamente igual que en original_main.py)
# ------------------------------------------------------------

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
    id: str  # MongoDB usa _id como string
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
    id: str  # MongoDB

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ------------------------------------------------------------
# Almacenamiento en memoria para tokens (sin cambios)
# ------------------------------------------------------------
active_tokens: Dict[str, int] = {}

# ------------------------------------------------------------
# Funciones auxiliares asíncronas para DB
# ------------------------------------------------------------
async def ensure_role_ids_exist(db: AsyncSession, role_ids: List[int]) -> None:
    if not role_ids:
        return
    stmt = select(RoleModel).where(RoleModel.id.in_(role_ids))
    result = await db.execute(stmt)
    existing_ids = {r.id for r in result.scalars().all()}
    missing = set(role_ids) - existing_ids
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Roles no encontrados: {list(missing)}",
        )

async def ensure_user_exists(db: AsyncSession, user_id: int) -> UserModel:
    user = await db.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

async def ensure_alert_for_user(db: AsyncSession, user_id: int, alert_id: int) -> AlertModel:
    alert = await db.get(AlertModel, alert_id)
    if not alert or alert.user_id != user_id:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    return alert

async def ensure_category_exists(db: AsyncSession, category_id: int) -> CategoryModel:
    category = await db.get(CategoryModel, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category

async def ensure_information_source_exists(db: AsyncSession, source_id: int) -> InformationSourceModel:
    source = await db.get(InformationSourceModel, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    return source

async def ensure_rss_for_source(db: AsyncSession, source_id: int, channel_id: int) -> RSSChannelModel:
    channel = await db.get(RSSChannelModel, channel_id)
    if not channel or channel.information_source_id != source_id:
        raise HTTPException(status_code=404, detail="Canal RSS no encontrado para la fuente")
    return channel

def sanitize_user(user: UserModel) -> User:
    return User(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        organization=user.organization,
        role_ids=user.role_ids or [],
    )

# ------------------------------------------------------------
# Dependencia de autenticación (sin cambios en lógica)
# ------------------------------------------------------------
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> UserModel:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Token inválido o ausente")

    user_id = active_tokens.get(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    user = await db.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario inválido")

    return user

# ------------------------------------------------------------
# Evento de inicio: crear tablas y datos semilla
# ------------------------------------------------------------
@app.on_event("startup")
async def on_startup():
    # Crear tablas si no existen (en producción usarías Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Insertar datos semilla si la tabla roles está vacía
    async with AsyncSession(engine) as db:
        result = await db.execute(select(RoleModel))
        if not result.scalars().first():
            admin_role = RoleModel(name="admin")
            user_role = RoleModel(name="user")
            db.add_all([admin_role, user_role])
            await db.flush()  # para obtener IDs

            admin_user = UserModel(
                email="admin@newsradar.com",
                first_name="Admin",
                last_name="NewsRadar",
                organization="NewsRadar",
                role_ids=[admin_role.id],
                password="admin123",  # En producción usar hash
            )
            db.add(admin_user)
            await db.commit()

# ------------------------------------------------------------
# Endpoints (misma estructura, pero con DB)
# ------------------------------------------------------------
@app.get(f"{API_PREFIX}/health", tags=["system"])
async def health() -> dict:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post(f"{API_PREFIX}/auth/login", response_model=TokenResponse, tags=["auth"])
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    stmt = select(UserModel).where(UserModel.email == payload.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = str(uuid4())
    active_tokens[token] = user.id
    return TokenResponse(access_token=token)

@app.post(f"{API_PREFIX}/auth/register", response_model=User, tags=["auth"])
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    stmt = select(UserModel).where(UserModel.email == payload.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    await ensure_role_ids_exist(db, payload.role_ids)

    user_db = UserModel(**payload.model_dump())
    db.add(user_db)
    await db.commit()
    await db.refresh(user_db)
    return sanitize_user(user_db)

@app.get(f"{API_PREFIX}/users", response_model=List[User], tags=["users"])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> List[User]:
    result = await db.execute(select(UserModel))
    users = result.scalars().all()
    return [sanitize_user(u) for u in users]

@app.post(f"{API_PREFIX}/users", response_model=User, status_code=201, tags=["users"])
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> User:
    stmt = select(UserModel).where(UserModel.email == payload.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    await ensure_role_ids_exist(db, payload.role_ids)

    user_db = UserModel(**payload.model_dump())
    db.add(user_db)
    await db.commit()
    await db.refresh(user_db)
    return sanitize_user(user_db)

@app.get(f"{API_PREFIX}/users/{{user_id}}", response_model=User, tags=["users"])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> User:
    user = await ensure_user_exists(db, user_id)
    return sanitize_user(user)

@app.put(f"{API_PREFIX}/users/{{user_id}}", response_model=User, tags=["users"])
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> User:
    user = await ensure_user_exists(db, user_id)

    data = payload.model_dump(exclude_unset=True)
    if "email" in data:
        stmt = select(UserModel).where(UserModel.email == data["email"], UserModel.id != user_id)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="El email ya está registrado")
    if "role_ids" in data:
        await ensure_role_ids_exist(db, data["role_ids"])

    for field, value in data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return sanitize_user(user)

@app.delete(
    f"{API_PREFIX}/users/{{user_id}}",
    status_code=204,
    response_class=Response,
    tags=["users"],
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    _: UserModel = Depends(get_current_user)
) -> None:
    user = await ensure_user_exists(db, user_id)

    # Obtener IDs de alertas del usuario
    stmt = select(AlertModel.id).where(AlertModel.user_id == user_id)
    result = await db.execute(stmt)
    alert_ids = [row[0] for row in result.all()]

    # Eliminar notificaciones asociadas en MongoDB
    if alert_ids:
        await mongo_db.notifications.delete_many({"alert_id": {"$in": alert_ids}})

    # Eliminar usuario (las alertas se eliminan en cascada por SQLAlchemy)
    await db.delete(user)
    await db.commit()

# ------------------------------------------------------------
# Roles
# ------------------------------------------------------------
@app.get(f"{API_PREFIX}/roles", response_model=List[Role], tags=["roles"])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> List[Role]:
    result = await db.execute(select(RoleModel))
    roles = result.scalars().all()
    return [Role(id=r.id, name=r.name) for r in roles]

@app.post(f"{API_PREFIX}/roles", response_model=Role, status_code=201, tags=["roles"])
async def create_role(
    payload: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> Role:
    role_db = RoleModel(**payload.model_dump())
    db.add(role_db)
    await db.commit()
    await db.refresh(role_db)
    return Role(id=role_db.id, name=role_db.name)

@app.get(f"{API_PREFIX}/roles/{{role_id}}", response_model=Role, tags=["roles"])
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> Role:
    role = await db.get(RoleModel, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return Role(id=role.id, name=role.name)

@app.put(f"{API_PREFIX}/roles/{{role_id}}", response_model=Role, tags=["roles"])
async def update_role(
    role_id: int,
    payload: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> Role:
    role = await db.get(RoleModel, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(role, field, value)

    await db.commit()
    await db.refresh(role)
    return Role(id=role.id, name=role.name)

@app.delete(
    f"{API_PREFIX}/roles/{{role_id}}",
    status_code=204,
    response_class=Response,
    tags=["roles"],
)
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> None:
    role = await db.get(RoleModel, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    # Verificar si el rol está asignado a algún usuario
    stmt = select(UserModel).where(UserModel.role_ids.contains([role_id]))
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar un rol asignado a usuarios",
        )

    await db.delete(role)
    await db.commit()

# ------------------------------------------------------------
# Alertas
# ------------------------------------------------------------
@app.get(
    f"{API_PREFIX}/users/{{user_id}}/alerts",
    response_model=List[Alert],
    tags=["alerts"],
)
async def list_user_alerts(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> List[Alert]:
    await ensure_user_exists(db, user_id)
    stmt = select(AlertModel).where(AlertModel.user_id == user_id)
    result = await db.execute(stmt)
    alerts = result.scalars().all()
    return [
        Alert(
            id=a.id,
            name=a.name,
            descriptors=a.descriptors or [],
            categories=a.categories or [],
            cron_expression=a.cron_expression,
            user_id=a.user_id,
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
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> Alert:
    await ensure_user_exists(db, user_id)

    alert_db = AlertModel(
        user_id=user_id,
        name=payload.name,
        descriptors=payload.descriptors,
        categories=[c.model_dump() for c in payload.categories],
        cron_expression=payload.cron_expression,
    )
    db.add(alert_db)
    await db.commit()
    await db.refresh(alert_db)

    return Alert(
        id=alert_db.id,
        name=alert_db.name,
        descriptors=alert_db.descriptors or [],
        categories=alert_db.categories or [],
        cron_expression=alert_db.cron_expression,
        user_id=alert_db.user_id,
    )

@app.get(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}",
    response_model=Alert,
    tags=["alerts"],
)
async def get_user_alert(
    user_id: int,
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> Alert:
    alert = await ensure_alert_for_user(db, user_id, alert_id)
    return Alert(
        id=alert.id,
        name=alert.name,
        descriptors=alert.descriptors or [],
        categories=alert.categories or [],
        cron_expression=alert.cron_expression,
        user_id=alert.user_id,
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
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> Alert:
    alert = await ensure_alert_for_user(db, user_id, alert_id)

    data = payload.model_dump(exclude_unset=True)
    if "categories" in data:
        data["categories"] = [c.model_dump() for c in payload.categories]

    for field, value in data.items():
        setattr(alert, field, value)

    await db.commit()
    await db.refresh(alert)

    return Alert(
        id=alert.id,
        name=alert.name,
        descriptors=alert.descriptors or [],
        categories=alert.categories or [],
        cron_expression=alert.cron_expression,
        user_id=alert.user_id,
    )

@app.delete(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}",
    status_code=204,
    response_class=Response,
    tags=["alerts"],
)
async def delete_user_alert(
    user_id: int,
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    _: UserModel = Depends(get_current_user)
) -> None:
    alert = await ensure_alert_for_user(db, user_id, alert_id)

    # Eliminar notificaciones asociadas en MongoDB
    await mongo_db.notifications.delete_many({"alert_id": alert_id})

    await db.delete(alert)
    await db.commit()

# ------------------------------------------------------------
# Notificaciones (MongoDB)
# ------------------------------------------------------------
@app.get(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications",
    response_model=List[Notification],
    tags=["notifications"],
)
async def list_alert_notifications(
    user_id: int,
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    _: UserModel = Depends(get_current_user)
) -> List[Notification]:
    await ensure_alert_for_user(db, user_id, alert_id)

    cursor = mongo_db.notifications.find({"alert_id": alert_id})
    notifications = []
    async for doc in cursor:
        notifications.append(
            Notification(
                id=str(doc["_id"]),
                alert_id=doc["alert_id"],
                timestamp=doc["timestamp"],
                metrics=doc.get("metrics", []),
            )
        )
    return notifications

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
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    _: UserModel = Depends(get_current_user)
) -> Notification:
    await ensure_alert_for_user(db, user_id, alert_id)

    doc = {
        "alert_id": alert_id,
        "timestamp": payload.timestamp,
        "metrics": [m.model_dump() for m in payload.metrics],
    }
    result = await mongo_db.notifications.insert_one(doc)
    doc["_id"] = result.inserted_id

    return Notification(
        id=str(doc["_id"]),
        alert_id=doc["alert_id"],
        timestamp=doc["timestamp"],
        metrics=doc.get("metrics", []),
    )

@app.get(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications/{{notification_id}}",
    response_model=Notification,
    tags=["notifications"],
)
async def get_alert_notification(
    user_id: int,
    alert_id: int,
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    _: UserModel = Depends(get_current_user)
) -> Notification:
    await ensure_alert_for_user(db, user_id, alert_id)

    from bson import ObjectId
    try:
        obj_id = ObjectId(notification_id)
    except:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    doc = await mongo_db.notifications.find_one({"_id": obj_id, "alert_id": alert_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Notificación no encontrada para la alerta")

    return Notification(
        id=str(doc["_id"]),
        alert_id=doc["alert_id"],
        timestamp=doc["timestamp"],
        metrics=doc.get("metrics", []),
    )

@app.put(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications/{{notification_id}}",
    response_model=Notification,
    tags=["notifications"],
)
async def update_alert_notification(
    user_id: int,
    alert_id: int,
    notification_id: str,
    payload: NotificationUpdate,
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    _: UserModel = Depends(get_current_user)
) -> Notification:
    await ensure_alert_for_user(db, user_id, alert_id)

    from bson import ObjectId
    try:
        obj_id = ObjectId(notification_id)
    except:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    update_data = {}
    if payload.timestamp is not None:
        update_data["timestamp"] = payload.timestamp
    if payload.metrics is not None:
        update_data["metrics"] = [m.model_dump() for m in payload.metrics]

    if update_data:
        await mongo_db.notifications.update_one(
            {"_id": obj_id, "alert_id": alert_id}, {"$set": update_data}
        )

    doc = await mongo_db.notifications.find_one({"_id": obj_id, "alert_id": alert_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Notificación no encontrada para la alerta")

    return Notification(
        id=str(doc["_id"]),
        alert_id=doc["alert_id"],
        timestamp=doc["timestamp"],
        metrics=doc.get("metrics", []),
    )

@app.delete(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications/{{notification_id}}",
    status_code=204,
    response_class=Response,
    tags=["notifications"],
)
async def delete_alert_notification(
    user_id: int,
    alert_id: int,
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    _: UserModel = Depends(get_current_user)
) -> None:
    await ensure_alert_for_user(db, user_id, alert_id)

    from bson import ObjectId
    try:
        obj_id = ObjectId(notification_id)
    except:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    result = await mongo_db.notifications.delete_one({"_id": obj_id, "alert_id": alert_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notificación no encontrada para la alerta")

# ------------------------------------------------------------
# Categorías
# ------------------------------------------------------------
@app.get(f"{API_PREFIX}/categories", response_model=List[Category], tags=["categories"])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> List[Category]:
    result = await db.execute(select(CategoryModel))
    categories = result.scalars().all()
    return [Category(id=c.id, name=c.name, source=c.source) for c in categories]

@app.post(f"{API_PREFIX}/categories", response_model=Category, status_code=201, tags=["categories"])
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> Category:
    cat_db = CategoryModel(**payload.model_dump())
    db.add(cat_db)
    await db.commit()
    await db.refresh(cat_db)
    return Category(id=cat_db.id, name=cat_db.name, source=cat_db.source)

@app.get(f"{API_PREFIX}/categories/{{category_id}}", response_model=Category, tags=["categories"])
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> Category:
    cat = await ensure_category_exists(db, category_id)
    return Category(id=cat.id, name=cat.name, source=cat.source)

@app.put(f"{API_PREFIX}/categories/{{category_id}}", response_model=Category, tags=["categories"])
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> Category:
    cat = await ensure_category_exists(db, category_id)

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(cat, field, value)

    await db.commit()
    await db.refresh(cat)
    return Category(id=cat.id, name=cat.name, source=cat.source)

@app.delete(
    f"{API_PREFIX}/categories/{{category_id}}",
    status_code=204,
    response_class=Response,
    tags=["categories"],
)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> None:
    cat = await ensure_category_exists(db, category_id)

    # Verificar si la categoría está asociada a canales RSS
    stmt = select(RSSChannelModel).where(RSSChannelModel.category_id == category_id)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Categoría asociada a canales RSS")

    await db.delete(cat)
    await db.commit()

# ------------------------------------------------------------
# Fuentes de información
# ------------------------------------------------------------
@app.get(
    f"{API_PREFIX}/information-sources",
    response_model=List[InformationSource],
    tags=["information-sources"],
)
async def list_information_sources(
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
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
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> InformationSource:
    source_db = InformationSourceModel(**payload.model_dump())
    db.add(source_db)
    await db.commit()
    await db.refresh(source_db)
    return InformationSource(id=source_db.id, name=source_db.name, url=source_db.url)

@app.get(
    f"{API_PREFIX}/information-sources/{{source_id}}",
    response_model=InformationSource,
    tags=["information-sources"],
)
async def get_information_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> InformationSource:
    source = await ensure_information_source_exists(db, source_id)
    return InformationSource(id=source.id, name=source.name, url=source.url)

@app.put(
    f"{API_PREFIX}/information-sources/{{source_id}}",
    response_model=InformationSource,
    tags=["information-sources"],
)
async def update_information_source(
    source_id: int,
    payload: InformationSourceUpdate,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> InformationSource:
    source = await ensure_information_source_exists(db, source_id)

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(source, field, value)

    await db.commit()
    await db.refresh(source)
    return InformationSource(id=source.id, name=source.name, url=source.url)

@app.delete(
    f"{API_PREFIX}/information-sources/{{source_id}}",
    status_code=204,
    response_class=Response,
    tags=["information-sources"],
)
async def delete_information_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> None:
    source = await ensure_information_source_exists(db, source_id)
    # Los canales RSS se eliminan en cascada (definido en modelos)
    await db.delete(source)
    await db.commit()

# ------------------------------------------------------------
# Canales RSS
# ------------------------------------------------------------
@app.get(
    f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels",
    response_model=List[RSSChannel],
    tags=["rss-channels"],
)
async def list_source_channels(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> List[RSSChannel]:
    await ensure_information_source_exists(db, source_id)

    stmt = select(RSSChannelModel).where(RSSChannelModel.information_source_id == source_id)
    result = await db.execute(stmt)
    channels = result.scalars().all()
    return [
        RSSChannel(
            id=c.id,
            url=c.url,
            category_id=c.category_id,
            information_source_id=c.information_source_id,
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
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> RSSChannel:
    await ensure_information_source_exists(db, source_id)
    await ensure_category_exists(db, payload.category_id)

    channel_db = RSSChannelModel(
        information_source_id=source_id,
        url=str(payload.url),
        category_id=payload.category_id,
    )
    db.add(channel_db)
    await db.commit()
    await db.refresh(channel_db)

    return RSSChannel(
        id=channel_db.id,
        url=channel_db.url,
        category_id=channel_db.category_id,
        information_source_id=channel_db.information_source_id,
    )

@app.get(
    f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels/{{channel_id}}",
    response_model=RSSChannel,
    tags=["rss-channels"],
)
async def get_source_channel(
    source_id: int,
    channel_id: int,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> RSSChannel:
    await ensure_information_source_exists(db, source_id)
    channel = await ensure_rss_for_source(db, source_id, channel_id)

    return RSSChannel(
        id=channel.id,
        url=channel.url,
        category_id=channel.category_id,
        information_source_id=channel.information_source_id,
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
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> RSSChannel:
    await ensure_information_source_exists(db, source_id)
    channel = await ensure_rss_for_source(db, source_id, channel_id)

    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data:
        await ensure_category_exists(db, data["category_id"])

    for field, value in data.items():
        if field == "url" and value is not None:
            value = str(value)
        setattr(channel, field, value)

    await db.commit()
    await db.refresh(channel)

    return RSSChannel(
        id=channel.id,
        url=channel.url,
        category_id=channel.category_id,
        information_source_id=channel.information_source_id,
    )

@app.delete(
    f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels/{{channel_id}}",
    status_code=204,
    response_class=Response,
    tags=["rss-channels"],
)
async def delete_source_channel(
    source_id: int,
    channel_id: int,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_user)
) -> None:
    await ensure_information_source_exists(db, source_id)
    channel = await ensure_rss_for_source(db, source_id, channel_id)

    await db.delete(channel)
    await db.commit()

# ------------------------------------------------------------
# Estadísticas (MongoDB)
# ------------------------------------------------------------
@app.get(f"{API_PREFIX}/stats", response_model=List[Stats], tags=["stats"])
async def list_stats(
    mongo_db=Depends(get_mongo_db),
    _: UserModel = Depends(get_current_user)
) -> List[Stats]:
    cursor = mongo_db.stats.find()
    stats_list = []
    async for doc in cursor:
        stats_list.append(
            Stats(
                id=str(doc["_id"]),
                metrics=doc.get("metrics", []),
            )
        )
    return stats_list

@app.post(f"{API_PREFIX}/stats", response_model=Stats, status_code=201, tags=["stats"])
async def create_stats(
    payload: StatsCreate,
    mongo_db=Depends(get_mongo_db),
    _: UserModel = Depends(get_current_user)
) -> Stats:
    doc = {
        "metrics": [m.model_dump() for m in payload.metrics],
    }
    result = await mongo_db.stats.insert_one(doc)
    doc["_id"] = result.inserted_id

    return Stats(
        id=str(doc["_id"]),
        metrics=doc["metrics"],
    )

@app.get(f"{API_PREFIX}/stats/{{stats_id}}", response_model=Stats, tags=["stats"])
async def get_stats(
    stats_id: str,
    mongo_db=Depends(get_mongo_db),
    _: UserModel = Depends(get_current_user)
) -> Stats:
    from bson import ObjectId
    try:
        obj_id = ObjectId(stats_id)
    except:
        raise HTTPException(status_code=404, detail="Stats no encontrados")

    doc = await mongo_db.stats.find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Stats no encontrados")

    return Stats(
        id=str(doc["_id"]),
        metrics=doc.get("metrics", []),
    )

@app.put(f"{API_PREFIX}/stats/{{stats_id}}", response_model=Stats, tags=["stats"])
async def update_stats(
    stats_id: str,
    payload: StatsUpdate,
    mongo_db=Depends(get_mongo_db),
    _: UserModel = Depends(get_current_user)
) -> Stats:
    from bson import ObjectId
    try:
        obj_id = ObjectId(stats_id)
    except:
        raise HTTPException(status_code=404, detail="Stats no encontrados")

    update_data = {}
    if payload.metrics is not None:
        update_data["metrics"] = [m.model_dump() for m in payload.metrics]

    if update_data:
        await mongo_db.stats.update_one({"_id": obj_id}, {"$set": update_data})

    doc = await mongo_db.stats.find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Stats no encontrados")

    return Stats(
        id=str(doc["_id"]),
        metrics=doc.get("metrics", []),
    )

@app.delete(
    f"{API_PREFIX}/stats/{{stats_id}}",
    status_code=204,
    response_class=Response,
    tags=["stats"],
)
async def delete_stats(
    stats_id: str,
    mongo_db=Depends(get_mongo_db),
    _: UserModel = Depends(get_current_user)
) -> None:
    from bson import ObjectId
    try:
        obj_id = ObjectId(stats_id)
    except:
        raise HTTPException(status_code=404, detail="Stats no encontrados")

    result = await mongo_db.stats.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Stats no encontrados")