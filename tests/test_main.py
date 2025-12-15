import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app, MOCK_TASKS, fetch_all_tasks, generate_productivity_report
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
async def test_get_all_tasks(reset_mock_tasks):
    """Test the /tasks endpoint returns all tasks."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/tasks")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 3
        assert tasks[0]["task_id"] == 1
        assert tasks[0]["title"] == "Refactor legacy service"
        assert tasks[0]["status"] == "complete"


@pytest.mark.asyncio
async def test_get_productivity_report(reset_mock_tasks):
    """Test the /report endpoint returns correct metrics."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/report")
        assert response.status_code == 200
        report = response.json()
        assert report["total_tasks"] == 3
        assert report["completed_tasks"] == 1
        assert report["total_hours_spent"] == 23.5
        assert report["completion_rate"] == 0.33


@pytest.mark.asyncio
async def test_log_task(reset_mock_tasks):
    """Test the /log_task endpoint creates a new task."""
    new_task = {
        "task_id": 0,  # Will be overridden
        "title": "Add new feature",
        "status": "pending",
        "hours_spent": 0.0
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/log_task", json=new_task)
        assert response.status_code == 200
        result = response.json()
        assert result["task_id"] == 4
        assert "logged successfully" in result["message"]
        assert len(MOCK_TASKS) == 4


@pytest.mark.asyncio
async def test_log_task_with_in_progress_status(reset_mock_tasks):
    """Test logging a task with IN_PROGRESS status."""
    new_task = {
        "task_id": 0,
        "title": "Debug production issue",
        "status": "in_progress",
        "hours_spent": 2.5
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/log_task", json=new_task)
        assert response.status_code == 200
        result = response.json()
        assert result["task_id"] == 4
        assert MOCK_TASKS[4].status == TaskStatus.IN_PROGRESS
        assert MOCK_TASKS[4].hours_spent == 2.5


@pytest.mark.asyncio
async def test_fetch_all_tasks_function(reset_mock_tasks):
    """Test the fetch_all_tasks utility function."""
    tasks = await fetch_all_tasks()
    assert len(tasks) == 3
    assert all(isinstance(task, DeveloperTask) for task in tasks)


@pytest.mark.asyncio
async def test_generate_productivity_report_function(reset_mock_tasks):
    """Test the generate_productivity_report utility function."""
    report = await generate_productivity_report()
    assert report.total_tasks == 3
    assert report.completed_tasks == 1
    assert report.total_hours_spent == 23.5
    assert report.completion_rate == 0.33


@pytest.mark.asyncio
async def test_productivity_report_with_no_tasks():
    """Test productivity report calculation with empty task list."""
    MOCK_TASKS.clear()
    report = await generate_productivity_report()
    assert report.total_tasks == 0
    assert report.completed_tasks == 0
    assert report.total_hours_spent == 0.0
    assert report.completion_rate == 0.0


@pytest.mark.asyncio
async def test_productivity_report_with_all_completed(reset_mock_tasks):
    """Test productivity report when all tasks are completed."""
    for task_id in MOCK_TASKS:
        MOCK_TASKS[task_id].status = TaskStatus.COMPLETE
    
    report = await generate_productivity_report()
    assert report.total_tasks == 3
    assert report.completed_tasks == 3
    assert report.completion_rate == 1.0
