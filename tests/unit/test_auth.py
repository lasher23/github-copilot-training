import pytest
from app.auth import verify_password, get_password_hash, get_user, authenticate_user


def test_password_hashing():
    """Test password hashing and verification."""
    password = "test_password"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


@pytest.mark.asyncio
async def test_get_user_exists():
    """Test retrieving an existing user."""
    user = await get_user("nicolas.schmid")
    
    assert user is not None
    assert user.username == "nicolas.schmid"
    assert user.email == "nicolas.schmid@accenture.com"
    assert "admin" in user.roles


@pytest.mark.asyncio
async def test_get_user_not_exists():
    """Test retrieving a non-existent user."""
    user = await get_user("nonexistent.user")
    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_valid_credentials():
    """Test authentication with valid credentials."""
    user = await authenticate_user("nicolas.schmid", "secret")
    
    assert user is not None
    assert user.username == "nicolas.schmid"


@pytest.mark.asyncio
async def test_authenticate_user_invalid_password():
    """Test authentication with invalid password."""
    user = await authenticate_user("nicolas.schmid", "wrong_password")
    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_nonexistent_user():
    """Test authentication with non-existent username."""
    user = await authenticate_user("nonexistent.user", "secret")
    assert user is None
