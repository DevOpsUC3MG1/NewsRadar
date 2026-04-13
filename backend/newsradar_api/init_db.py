"""
Script para inicializar la base de datos PostgreSQL con el esquema correcto.
Ejecutar con: python init_db.py
"""
import asyncio
import sys
from pathlib import Path
from uuid import uuid4

# Añadir el directorio app al path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.database import DATABASE_URL, Base
from app.models import User, Role, Alert, Category, InformationSource, RSSChannel


async def init_database():
    """Crear todas las tablas en la base de datos"""
    print(f"Conectando a: {DATABASE_URL}")
    
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        print("Eliminando tablas existentes...")
        await conn.run_sync(Base.metadata.drop_all)
        
        print("Creando nuevas tablas...")
        await conn.run_sync(Base.metadata.create_all)
    
    print("Creando datos semilla...")
    async with AsyncSession(engine, expire_on_commit=False) as session:
        # Crear roles
        admin_role = Role(name="admin")
        user_role = Role(name="user")
        session.add(admin_role)
        session.add(user_role)
        await session.flush()
        
        # Guardar IDs antes del commit
        admin_role_id = admin_role.id
        user_role_id = user_role.id
        
        # Crear usuario admin
        admin_user = User(
            email="admin@newsradar.com",
            first_name="Admin",
            last_name="NewsRadar",
            organization="NewsRadar",
            password="admin123",
            role_ids=[admin_role_id],
            is_verified=True
        )
        session.add(admin_user)
        
        await session.commit()
        print(f"✓ Usuario admin creado con email: admin@newsradar.com")
        print(f"✓ Roles creados: admin (ID: {admin_role_id}), user (ID: {user_role_id})")
    
    await engine.dispose()
    print("\n✅ Base de datos inicializada correctamente!")
    print("\nCredenciales de acceso:")
    print("  Email: admin@newsradar.com")
    print("  Password: admin123")


if __name__ == "__main__":
    asyncio.run(init_database())