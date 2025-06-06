"""Main FastAPI application module."""
import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

from app.core.config import settings
from app.core.database import init_db
from app.health import router as health_router
from app.routers.flights import router as flights_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Custom JSON encoder function for MongoDB ObjectId
def custom_jsonable_encoder(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return jsonable_encoder(obj)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Flight management API with FastAPI and MongoDB",
    docs_url="/docs",
    redoc_url="/redoc",
    default_response_class=JSONResponse,
    json_encoders={ObjectId: str}
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(flights_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    logger.info("Starting up application...")
    await init_db()
    logger.info("Database initialized")

    # Seed database if environment variable is set
    if os.environ.get("SEED_DATA", "").lower() == "true":
        logger.info("Seeding database with initial data...")
        try:
            from app.scripts.seed_data import seed_database
            await seed_database()
            logger.info("Database seeding completed")
        except Exception as e:
            logger.error(f"Error seeding database: {e}", exc_info=True)

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    logger.info("Shutting down application...")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name} v{settings.app_version}",
        "docs": "/docs",
    }
