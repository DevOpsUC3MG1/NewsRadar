from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import create_engine, text
import os
from app.schemas.alert import AlertaCreate, AlertaResponse
import uuid
from datetime import datetime

app = FastAPI(title="NewsRadar API", version="0.1.0")

# Configuración desde variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/newsradar")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

@app.get("/health")
async def health():
    """Verifica la salud del sistema para el Pipeline de CI/CD"""
    status = {"api": "ok", "databases": {}}
    try:
        # Test Postgres
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        status["databases"]["postgres"] = "connected"
        
        # Test Mongo
        client = AsyncIOMotorClient(MONGO_URL)
        await client.admin.command('ping')
        status["databases"]["mongodb"] = "connected"
    except Exception as e:
        status["api"] = "error"
        raise HTTPException(status_code=500, detail=str(e))
    return status

@app.post("/api/v1/alerts", response_model=AlertaResponse, tags=["Alertas"])
async def create_mock_alert(alerta: AlertaCreate):
    """Mock para que Frontend pueda empezar a trabajar en la S0"""
    return {
        **alerta.model_dump(),
        "id": str(uuid.uuid4()),
        "user_id": "user_demo_001",
        "descriptores_ia": [alerta.palabra_clave, "ia-keyword-1", "ia-keyword-2"],
        "created_at": datetime.now(),
        "is_active": True
    }