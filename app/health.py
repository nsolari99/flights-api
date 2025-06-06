"""Health check endpoint for the API."""
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.core.database import init_db

router = APIRouter(tags=["Health"])


async def get_db_client():
    """Get database client for dependency injection."""
    client = AsyncIOMotorClient(settings.mongodb_url)
    try:
        yield client
    finally:
        client.close()


@router.get("/health")
async def health_check(client: AsyncIOMotorClient = Depends(get_db_client)):
    """Health check endpoint to verify API and database are operational."""
    try:
        # Check database connection
        await client.admin.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "database": db_status
    }
