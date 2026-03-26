from fastapi import FastAPI
from app.routers import auth
# from app.routers import alerts, sources (Se añadirán en S2/S3)

app = FastAPI(
    title="NewsRadar API",
    description="Sistema de monitorización con persistencia dual",
    version="1.0.0"
)

# Incluir los routers modularizados
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación"])

@app.get("/api/v1/config", tags=["Infraestructura"])
async def get_feature_flags():
    """ Cumple con ASR-04 y ADR-006: Exponer Feature Flags al Frontend """
    import os
    return {
        "wordcloud_enabled": os.getenv("FEATURE_WORDCLOUD_ENABLED", "true").lower() == "true",
        "ia_suggestions_enabled": os.getenv("FEATURE_IA_ENABLED", "true").lower() == "true"
    }