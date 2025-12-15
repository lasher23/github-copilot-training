import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_status(client: AsyncClient):
    """Test the /status endpoint returns ok status."""
    response = await client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login returns access token."""
    response = await client.post(
        "/token",
        data={"username": "nicolas.schmid", "password": "secret"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials returns 401."""
    response = await client.post(
        "/token",
        data={"username": "nicolas.schmid", "password": "wrong"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_tasks_authenticated(client: AsyncClient, auth_token: str):
    """Test the /tasks endpoint returns all tasks with authentication."""
    # Get tasks
    response = await client.get(
        "/tasks",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 3
    assert tasks[0]["task_id"] == 1
    assert tasks[0]["title"] == "Refactor legacy service"


@pytest.mark.asyncio
async def test_get_all_tasks_unauthenticated(client: AsyncClient):
    """Test the /tasks endpoint requires authentication."""
    response = await client.get("/tasks")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_productivity_report_authenticated(client: AsyncClient, auth_token: str):
    """Test the /report endpoint returns correct metrics with authentication."""
    # Get report
    response = await client.get(
        "/report",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    report = response.json()
    assert report["total_tasks"] == 3
    assert report["completed_tasks"] == 1
    assert report["total_hours_spent"] == 23.5
    assert report["completion_rate"] == 0.33


@pytest.mark.asyncio
async def test_log_task_authenticated(client: AsyncClient, auth_token: str):
    """Test the /log_task endpoint creates a new task with authentication."""
    new_task = {
        "task_id": 0,
        "title": "Add new feature",
        "status": "pending",
        "hours_spent": 0.0
    }
    
    # Log task
    response = await client.post(
        "/log_task",
        json=new_task,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    result = response.json()
    assert result["task_id"] == 4
    assert "logged successfully" in result["message"]
    
    # Verify task was created
    get_response = await client.get(
        "/tasks",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    tasks = get_response.json()
    assert len(tasks) == 4


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_token: str):
    """Test the /users/me endpoint returns current user info."""
    # Get user info
    response = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == "nicolas.schmid"
    assert user["email"] == "nicolas.schmid@accenture.com"
    assert "admin" in user["roles"]
