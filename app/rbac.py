from typing import Dict, List, Set
from fastapi import HTTPException, status
from app.models import Role, User

# Mock RBAC Configuration
PERMISSIONS: Dict[str, str] = {
    "task:create": "Create new tasks",
    "task:view": "View tasks",
    "task:update": "Update existing tasks",
    "task:delete": "Delete tasks",
    "report:view": "View productivity reports",
    "report:generate": "Generate productivity reports",
    "user:view": "View user information",
}

ROLES: Dict[str, Role] = {
    "admin": Role(
        name="admin",
        permissions=list(PERMISSIONS.keys()),  # All permissions
        description="Administrator with full access"
    ),
    "developer": Role(
        name="developer",
        permissions=[
            "task:create",
            "task:view",
            "task:update",
            "report:view",
            "user:view",
        ],
        description="Developer who can manage their own tasks"
    ),
    "viewer": Role(
        name="viewer",
        permissions=[
            "task:view",
            "report:view",
            "user:view",
        ],
        description="Read-only access to tasks and reports"
    ),
    "manager": Role(
        name="manager",
        permissions=[
            "task:view",
            "task:update",
            "task:delete",
            "report:view",
            "report:generate",
            "user:view",
        ],
        description="Manager who can view and manage all tasks"
    ),
}


def get_user_permissions(user: User) -> Set[str]:
    """
    Aggregate all permissions from user's roles.
    Returns a set of permission names.
    """
    permissions: Set[str] = set()
    for role_name in user.roles:
        role = ROLES.get(role_name)
        if role:
            permissions.update(role.permissions)
    return permissions


def has_permission(user: User, required_permission: str) -> bool:
    """Check if user has a specific permission."""
    user_permissions = get_user_permissions(user)
    return required_permission in user_permissions


def require_permission(user: User, required_permission: str) -> None:
    """
    Raise HTTPException if user doesn't have required permission.
    Use this in dependencies or route handlers.
    """
    if not has_permission(user, required_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied. Required permission: {required_permission}"
        )


def has_any_permission(user: User, required_permissions: List[str]) -> bool:
    """Check if user has at least one of the required permissions."""
    user_permissions = get_user_permissions(user)
    return any(perm in user_permissions for perm in required_permissions)


def has_all_permissions(user: User, required_permissions: List[str]) -> bool:
    """Check if user has all of the required permissions."""
    user_permissions = get_user_permissions(user)
    return all(perm in user_permissions for perm in required_permissions)
