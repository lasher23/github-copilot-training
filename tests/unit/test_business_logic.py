import pytest
from app.main import fetch_all_tasks, generate_productivity_report, MOCK_TASKS
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
