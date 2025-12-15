import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_has_all_permissions(client: AsyncClient):
    """Test that admin role has all permissions via API."""
    response = await client.post(
        "/token",
        data={"username": "nicolas.schmid", "password": "secret"}
    )
    token = response.json()["access_token"]
    
    response = await client.get(
        "/users/me/permissions",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    permissions = response.json()
    assert "task:create" in permissions
    assert "task:delete" in permissions
    assert "report:generate" in permissions


@pytest.mark.asyncio
async def test_developer_can_create_tasks(client: AsyncClient):
    """Test that developer role can create tasks via API."""
    response = await client.post(
        "/token",
        data={"username": "john.developer", "password": "secret"}
    )
    token = response.json()["access_token"]
    
    new_task = {
        "task_id": 0,
        "title": "New feature",
        "status": "pending",
        "hours_spent": 0.0
    }
    
    response = await client.post(
        "/log_task",
        json=new_task,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_viewer_cannot_create_tasks(client: AsyncClient):
    """Test that viewer role cannot create tasks (403 Forbidden)."""
    response = await client.post(
        "/token",
        data={"username": "jane.viewer", "password": "secret"}
    )
    token = response.json()["access_token"]
    
    new_task = {
        "task_id": 0,
        "title": "Should fail",
        "status": "pending",
        "hours_spent": 0.0
    }
    
    response = await client.post(
        "/log_task",
        json=new_task,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "Permission denied" in response.json()["detail"]


@pytest.mark.asyncio
async def test_viewer_can_view_tasks(client: AsyncClient):
    """Test that viewer role can view tasks via API."""
    response = await client.post(
        "/token",
        data={"username": "jane.viewer", "password": "secret"}
    )
    token = response.json()["access_token"]
    
    response = await client.get(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_all_roles(client: AsyncClient):
    """Test the /roles endpoint returns all role definitions."""
    response = await client.post(
        "/token",
        data={"username": "nicolas.schmid", "password": "secret"}
    )
    token = response.json()["access_token"]
    
    response = await client.get(
        "/roles",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    roles = response.json()
    assert len(roles) == 4
    role_names = [r["name"] for r in roles]
    assert "admin" in role_names
    assert "developer" in role_names
    assert "viewer" in role_names
    assert "manager" in role_names


@pytest.mark.asyncio
async def test_manager_permissions(client: AsyncClient):
    """Test that manager has correct permissions."""
    response = await client.post(
        "/token",
        data={"username": "bob.manager", "password": "secret"}
    )
    token = response.json()["access_token"]
    
    response = await client.get(
        "/users/me/permissions",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    permissions = response.json()
    assert "task:view" in permissions
    assert "task:update" in permissions
    assert "task:delete" in permissions
    assert "report:generate" in permissions
    assert "task:create" not in permissions  # Manager cannot create
