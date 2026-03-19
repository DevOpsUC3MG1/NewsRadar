from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class AlertaBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100, example="Crisis Energética")
    palabra_clave: str = Field(..., example="gas natural")
    frecuencia_cron: str = Field(..., example="0 */6 * * *") 
    fuentes_ids: List[str] = Field(default=[], description="IDs de los canales RSS")
    categoria_iptc: str = Field(..., example="04000000")

class AlertaCreate(AlertaBase):
    pass

class AlertaResponse(AlertaBase):
    id: str
    user_id: str
    descriptores_ia: List[str] = []
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True