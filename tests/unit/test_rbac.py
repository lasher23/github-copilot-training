import pytest
from app.rbac import (
    get_user_permissions,
    has_permission,
    has_any_permission,
    has_all_permissions,
    require_permission,
    ROLES,
    PERMISSIONS
)
from app.models import User
from fastapi import HTTPException


def test_get_user_permissions_single_role():
    """Test permission aggregation from a single role."""
    user = User(
        username="test",
        email="test@test.com",
        roles=["viewer"]
    )
    permissions = get_user_permissions(user)
    
    assert "task:view" in permissions
    assert "report:view" in permissions
    assert "task:create" not in permissions


def test_get_user_permissions_multiple_roles():
    """Test permission aggregation from multiple roles."""
    user = User(
        username="test",
        email="test@test.com",
        roles=["developer", "viewer"]
    )
    permissions = get_user_permissions(user)
    
    assert "task:view" in permissions
    assert "task:create" in permissions
    assert "task:update" in permissions


def test_get_user_permissions_admin():
    """Test that admin role has all permissions."""
    user = User(
        username="test",
        email="test@test.com",
        roles=["admin"]
    )
    permissions = get_user_permissions(user)
    
    assert len(permissions) == len(PERMISSIONS)
    assert "task:create" in permissions
    assert "task:delete" in permissions
    assert "report:generate" in permissions


def test_has_permission_with_permission():
    """Test has_permission returns True when user has permission."""
    user = User(
        username="test",
        email="test@test.com",
        roles=["viewer"]
    )
    assert has_permission(user, "task:view") is True


def test_has_permission_without_permission():
    """Test has_permission returns False when user lacks permission."""
    user = User(
        username="test",
        email="test@test.com",
        roles=["viewer"]
    )
    assert has_permission(user, "task:create") is False


def test_has_any_permission_true():
    """Test has_any_permission returns True when user has at least one permission."""
    user = User(
        username="test",
        email="test@test.com",
        roles=["viewer"]
    )
    assert has_any_permission(user, ["task:view", "task:create"]) is True


def test_has_any_permission_false():
    """Test has_any_permission returns False when user has none of the permissions."""
    user = User(
        username="test",
        email="test@test.com",
        roles=["viewer"]
    )
    assert has_any_permission(user, ["task:create", "task:delete"]) is False


def test_has_all_permissions_true():
    """Test has_all_permissions returns True when user has all permissions."""
    user = User(
        username="test",
        email="test@test.com",
        roles=["developer"]
    )
    assert has_all_permissions(user, ["task:view", "task:create"]) is True


def test_has_all_permissions_false():
    """Test has_all_permissions returns False when user lacks any permission."""
    user = User(
        username="test",
        email="test@test.com",
        roles=["viewer"]
    )
    assert has_all_permissions(user, ["task:view", "task:create"]) is False


def test_require_permission_success():
    """Test require_permission does not raise when user has permission."""
    user = User(
        username="test",
        email="test@test.com",
        roles=["developer"]
    )
    # Should not raise
    require_permission(user, "task:create")


def test_require_permission_failure():
    """Test require_permission raises HTTPException when user lacks permission."""
    user = User(
        username="test",
        email="test@test.com",
        roles=["viewer"]
    )
    
    with pytest.raises(HTTPException) as exc_info:
        require_permission(user, "task:create")
    
    assert exc_info.value.status_code == 403
    assert "Permission denied" in exc_info.value.detail


def test_roles_configuration():
    """Test that all roles are properly configured."""
    assert "admin" in ROLES
    assert "developer" in ROLES
    assert "viewer" in ROLES
    assert "manager" in ROLES
    
    admin_role = ROLES["admin"]
    assert len(admin_role.permissions) == len(PERMISSIONS)
