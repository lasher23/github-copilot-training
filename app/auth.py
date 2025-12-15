from datetime import datetime, timedelta, timezone
from typing import Dict, Any
import bcrypt
from jose import JWTError, jwt
from app.models import User, UserInDB

# Security configuration - Keep SECRET_KEY under 72 bytes
SECRET_KEY = "your-secret-key-change-in-production-min-32-chars"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Mock user database - password is "secret"
MOCK_USERS: Dict[str, UserInDB] = {
    "nicolas.schmid": UserInDB(
        username="nicolas.schmid",
        email="nicolas.schmid@accenture.com",
        full_name="Nicolas Schmid",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        disabled=False,
        roles=["admin"]
    ),
    "john.developer": UserInDB(
        username="john.developer",
        email="john.developer@accenture.com",
        full_name="John Developer",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        disabled=False,
        roles=["developer"]
    ),
    "jane.viewer": UserInDB(
        username="jane.viewer",
        email="jane.viewer@accenture.com",
        full_name="Jane Viewer",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        disabled=False,
        roles=["viewer"]
    ),
    "bob.manager": UserInDB(
        username="bob.manager",
        email="bob.manager@accenture.com",
        full_name="Bob Manager",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        disabled=False,
        roles=["manager"]
    ),
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Hash a password for storage."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


async def get_user(username: str) -> UserInDB | None:
    """Retrieve user from mock database."""
    return MOCK_USERS.get(username)


async def authenticate_user(username: str, password: str) -> UserInDB | None:
    """Authenticate user credentials."""
    user = await get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
