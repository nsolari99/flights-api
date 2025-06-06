"""Database connection and initialization module."""
from typing import List, Type

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.models.flight import Flight


async def init_db():
    """Initialize database connection and register document models."""
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client.get_default_database()
    
    # Register all document models with Beanie
    document_models: List[Type] = [Flight]
    await init_beanie(database=db, document_models=document_models)
    
    return client
