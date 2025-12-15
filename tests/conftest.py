"""Pytest configuration and shared fixtures."""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

from app.main import app


# Use a test database
TEST_MONGODB_URL = os.getenv("TEST_MONGODB_URL", "mongodb://localhost:27017")
TEST_DATABASE_NAME = "productivity_app_test"


async def _test_mongodb_connection() -> bool:
    """Test if MongoDB is available."""
    try:
        client = AsyncIOMotorClient(TEST_MONGODB_URL, serverSelectionTimeoutMS=2000)
        await client.admin.command('ping')
        client.close()
        return True
    except Exception:
        return False


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create a clean test database for each test."""
    # Check if MongoDB is available
    if not await _test_mongodb_connection():
        pytest.skip("MongoDB is not available. Start MongoDB or set TEST_MONGODB_URL environment variable.")
    
    # Override environment variables for testing
    os.environ["MONGODB_URL"] = TEST_MONGODB_URL
    os.environ["DATABASE_NAME"] = TEST_DATABASE_NAME
    
    # Import here to ensure env vars are set before module initialization
    from app.database import connect_to_mongodb, close_mongodb_connection, get_database
    from app.services.task_service import seed_tasks
    from app.services.user_service import seed_users
    
    # Connect to test database
    await connect_to_mongodb()
    db = get_database()
    
    # Clear all collections before test
    for collection_name in await db.list_collection_names():
        await db[collection_name].delete_many({})
    
    # Seed test data
    await seed_users()
    await seed_tasks()
    
    yield db
    
    # Clean up after test
    for collection_name in await db.list_collection_names():
        await db[collection_name].delete_many({})
    
    await close_mongodb_connection()


@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    """Create an async HTTP client for testing."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def auth_token(client):
    """Get an authentication token for testing."""
    response = await client.post(
        "/token",
        data={"username": "nicolas.schmid", "password": "secret"}
    )
    return response.json()["access_token"]
