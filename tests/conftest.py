"""Test fixtures for the flights API."""
import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.core.database import init_beanie
from app.main import app
from app.models.flight import Flight


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db_client() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Create a MongoDB client for testing."""
    # Use a test database
    test_db_url = os.environ.get("TEST_MONGODB_URL", "mongodb://localhost:27017/test_flights")
    client = AsyncIOMotorClient(test_db_url)
    
    # Initialize Beanie with test database
    db = client.get_default_database()
    await init_beanie(database=db, document_models=[Flight])
    
    yield client
    
    # Clean up after tests
    await client.drop_database(db)
    client.close()


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Create a FastAPI test client."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(autouse=True)
async def clear_db(db_client: AsyncIOMotorClient) -> None:
    """Clear the database before each test."""
    db = db_client.get_default_database()
    await db.flights.delete_many({})
