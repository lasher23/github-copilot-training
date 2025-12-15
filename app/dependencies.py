from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.auth import SECRET_KEY, ALGORITHM, get_user
from app.models import User, TokenData
from typing import List
from app.rbac import require_permission

# FastAPI's built-in OAuth2 scheme - automatically adds authentication UI to /docs
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    FastAPI dependency that extracts and validates the JWT token.
    Automatically enforces authentication on any endpoint that uses it.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    # Return User with roles included
    return User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        disabled=user.disabled,
        roles=user.roles
    )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Additional dependency to check if user account is active."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


class PermissionChecker:
    """
    Dependency class for checking user permissions.
    Usage: Depends(PermissionChecker(["task:create"]))
    """
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions
    
    async def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        for permission in self.required_permissions:
            require_permission(current_user, permission)
        return current_user
