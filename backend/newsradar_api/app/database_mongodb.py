import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Conexión a Mongo. Por defecto a localhost para desarrollo local.
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGO_URL)
db_mongo = client.newsradar_archive

# Dependencia para FastAPI


def get_mongo_db():
    return db_mongo
