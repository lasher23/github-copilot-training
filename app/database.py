"""MongoDB database configuration and connection management."""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os


# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "productivity_app")

# Global client instance
_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongodb() -> None:
    """Establish connection to MongoDB."""
    global _client, _database
    _client = AsyncIOMotorClient(MONGODB_URL)
    _database = _client[DATABASE_NAME]


async def close_mongodb_connection() -> None:
    """Close MongoDB connection."""
    global _client
    if _client:
        _client.close()


def get_database() -> AsyncIOMotorDatabase:
    """Get the database instance."""
    if _database is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongodb() first.")
    return _database
