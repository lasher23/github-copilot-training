"""Pytest configuration and shared fixtures."""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
from testcontainers.mongodb import MongoDbContainer
import time

# Use a test database
TEST_DATABASE_NAME = "productivity_app_test"

# Global MongoDB container instance
_mongodb_container = None


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables before any imports."""
    # Check if TEST_MONGODB_URL is provided (for CI/CD or external MongoDB)
    if os.getenv("TEST_MONGODB_URL"):
        os.environ["MONGODB_URL"] = os.getenv("TEST_MONGODB_URL")
        os.environ["DATABASE_NAME"] = TEST_DATABASE_NAME
        yield
        return
    
    global _mongodb_container
    
    try:
        # Start MongoDB container
        _mongodb_container = MongoDbContainer("mongo:7.0")
        _mongodb_container.start()
        
        # Get connection URL
        connection_url = _mongodb_container.get_connection_url()
        
        # Set environment variables for the test session
        os.environ["MONGODB_URL"] = connection_url
        os.environ["DATABASE_NAME"] = TEST_DATABASE_NAME
        
        yield
        
    except Exception as e:
        # If container startup fails, skip all tests with informative message
        pytest.skip(
            f"MongoDB container could not be started. Docker may not be available or there was a container issue. "
            f"Error: {str(e)}. Set TEST_MONGODB_URL environment variable to use external MongoDB."
        )
    finally:
        # Stop and remove container after all tests
        if _mongodb_container:
            try:
                _mongodb_container.stop()
            except Exception:
                pass  # Ignore cleanup errors


# Import app after environment is configured
@pytest.fixture(scope="session")
def app(setup_test_environment):
    """Get the FastAPI app instance."""
    from app.main import app
    return app


@pytest_asyncio.fixture(scope="function")
async def test_db(setup_test_environment):
    """Create a clean test database for each test."""
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
async def client(test_db, app):
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
