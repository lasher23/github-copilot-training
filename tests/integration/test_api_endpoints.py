import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app, MOCK_TASKS
from app.models import DeveloperTask, TaskStatus


@pytest.fixture
def reset_mock_tasks():
    """Reset MOCK_TASKS to initial state before each test."""
    MOCK_TASKS.clear()
    MOCK_TASKS.update({
        1: DeveloperTask(task_id=1, title="Refactor legacy service", status=TaskStatus.COMPLETE, hours_spent=8.5),
        2: DeveloperTask(task_id=2, title="Implement new user auth flow", status=TaskStatus.IN_PROGRESS, hours_spent=15.0),
        3: DeveloperTask(task_id=3, title="Write unit tests for checkout", status=TaskStatus.PENDING, hours_spent=0.0),
    })
    yield
    MOCK_TASKS.clear()


@pytest.mark.asyncio
async def test_get_status():
    """Test the /status endpoint returns ok status."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/status")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_login_success():
    """Test successful login returns access token."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/token",
            data={"username": "nicolas.schmid", "password": "secret"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with invalid credentials returns 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/token",
            data={"username": "nicolas.schmid", "password": "wrong"}
        )
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_tasks_authenticated(reset_mock_tasks):
    """Test the /tasks endpoint returns all tasks with authentication."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/token",
            data={"username": "nicolas.schmid", "password": "secret"}
        )
        token = login_response.json()["access_token"]
        
        # Get tasks
        response = await client.get(
            "/tasks",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 3
        assert tasks[0]["task_id"] == 1
        assert tasks[0]["title"] == "Refactor legacy service"


@pytest.mark.asyncio
async def test_get_all_tasks_unauthenticated(reset_mock_tasks):
    """Test the /tasks endpoint requires authentication."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/tasks")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_productivity_report_authenticated(reset_mock_tasks):
    """Test the /report endpoint returns correct metrics with authentication."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/token",
            data={"username": "nicolas.schmid", "password": "secret"}
        )
        token = login_response.json()["access_token"]
        
        # Get report
        response = await client.get(
            "/report",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        report = response.json()
        assert report["total_tasks"] == 3
        assert report["completed_tasks"] == 1
        assert report["total_hours_spent"] == 23.5
        assert report["completion_rate"] == 0.33


@pytest.mark.asyncio
async def test_log_task_authenticated(reset_mock_tasks):
    """Test the /log_task endpoint creates a new task with authentication."""
    new_task = {
        "task_id": 0,
        "title": "Add new feature",
        "status": "pending",
        "hours_spent": 0.0
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/token",
            data={"username": "nicolas.schmid", "password": "secret"}
        )
        token = login_response.json()["access_token"]
        
        # Log task
        response = await client.post(
            "/log_task",
            json=new_task,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        result = response.json()
        assert result["task_id"] == 4
        assert "logged successfully" in result["message"]
        assert len(MOCK_TASKS) == 4


@pytest.mark.asyncio
async def test_get_current_user():
    """Test the /users/me endpoint returns current user info."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Login
        login_response = await client.post(
            "/token",
            data={"username": "nicolas.schmid", "password": "secret"}
        )
        token = login_response.json()["access_token"]
        
        # Get user info
        response = await client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        user = response.json()
        assert user["username"] == "nicolas.schmid"
        assert user["email"] == "nicolas.schmid@accenture.com"
        assert "admin" in user["roles"]
