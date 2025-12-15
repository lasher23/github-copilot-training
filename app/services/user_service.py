"""Service layer for user operations with MongoDB."""
from typing import Optional
from app.models import UserInDB
from app.database import get_database


async def get_user(username: str) -> Optional[UserInDB]:
    """Retrieve user from MongoDB."""
    db = get_database()
    users_collection = db["users"]
    
    user_doc = await users_collection.find_one({"username": username})
    if user_doc:
        user_doc.pop("_id", None)
        return UserInDB(**user_doc)
    return None


async def create_user(user: UserInDB) -> UserInDB:
    """Create a new user in MongoDB."""
    db = get_database()
    users_collection = db["users"]
    
    user_dict = user.model_dump()
    await users_collection.insert_one(user_dict)
    return user


async def seed_users() -> None:
    """Seed initial user data to MongoDB."""
    db = get_database()
    users_collection = db["users"]
    
    # Check if users already exist
    existing_count = await users_collection.count_documents({})
    if existing_count > 0:
        return  # Don't seed if data already exists
    
    # Mock users - password is "secret" (hashed)
    initial_users = [
        {
            "username": "nicolas.schmid",
            "email": "nicolas.schmid@accenture.com",
            "full_name": "Nicolas Schmid",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            "disabled": False,
            "roles": ["admin"]
        },
        {
            "username": "john.developer",
            "email": "john.developer@accenture.com",
            "full_name": "John Developer",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            "disabled": False,
            "roles": ["developer"]
        },
        {
            "username": "jane.viewer",
            "email": "jane.viewer@accenture.com",
            "full_name": "Jane Viewer",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            "disabled": False,
            "roles": ["viewer"]
        },
        {
            "username": "bob.manager",
            "email": "bob.manager@accenture.com",
            "full_name": "Bob Manager",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            "disabled": False,
            "roles": ["manager"]
        }
    ]
    
    await users_collection.insert_many(initial_users)
