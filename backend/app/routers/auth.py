from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

# Esquema de entrada temporal (luego se moverá a schemas/)
class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login", summary="Autenticación de usuario")
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    TODO (Para M2): 
    1. Buscar usuario en base de datos por email.
    2. Verificar hash de contraseña (Bcrypt).
    3. Generar y devolver JWT Token.
    """
    # Ejemplo práctico de respuesta esperada por el Frontend
    return {
        "access_token": "token_jwt_simulado_aqui",
        "token_type": "bearer"
    }