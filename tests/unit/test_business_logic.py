import pytest
from app.main import generate_productivity_report
from app.models import DeveloperTask, TaskStatus
from app.services.task_service import get_all_tasks, create_task
from app.database import get_database


@pytest.mark.asyncio
async def test_fetch_all_tasks_function(test_db):
    """Test the get_all_tasks service function."""
    tasks = await get_all_tasks()
    assert len(tasks) == 3
    assert all(isinstance(task, DeveloperTask) for task in tasks)


@pytest.mark.asyncio
async def test_generate_productivity_report_function(test_db):
    """Test the generate_productivity_report utility function."""
    report = await generate_productivity_report()
    assert report.total_tasks == 3
    assert report.completed_tasks == 1
    assert report.total_hours_spent == 23.5
    assert report.completion_rate == 0.33


@pytest.mark.asyncio
async def test_productivity_report_with_no_tasks(test_db):
    """Test productivity report calculation with empty task list."""
    db = get_database()
    await db["tasks"].delete_many({})
    
    report = await generate_productivity_report()
    assert report.total_tasks == 0
    assert report.completed_tasks == 0
    assert report.total_hours_spent == 0.0
    assert report.completion_rate == 0.0


@pytest.mark.asyncio
async def test_productivity_report_with_all_completed(test_db):
    """Test productivity report when all tasks are completed."""
    db = get_database()
    await db["tasks"].update_many(
        {},
        {"$set": {"status": TaskStatus.COMPLETE.value}}
    )
    
    report = await generate_productivity_report()
    assert report.total_tasks == 3
    assert report.completed_tasks == 3
    assert report.completion_rate == 1.0
