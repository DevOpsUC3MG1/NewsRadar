from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# NOTA LEAD: Usamos postgresql+asyncpg para cumplir con el ADR-003 (asincronía)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://admin:password123@localhost:5432/newsradar_core")

engine = create_async_engine(DATABASE_URL, echo=False)

# Creador de sesiones asíncronas para inyectar en los endpoints
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# Dependencia para FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session