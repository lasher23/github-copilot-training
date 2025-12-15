"""Service layer for task operations with MongoDB."""
from typing import List, Optional
from app.models import DeveloperTask, TaskStatus
from app.database import get_database


async def get_all_tasks() -> List[DeveloperTask]:
    """Fetch all tasks from MongoDB."""
    db = get_database()
    tasks_collection = db["tasks"]
    
    cursor = tasks_collection.find({})
    tasks = []
    async for task_doc in cursor:
        # Remove MongoDB _id field
        task_doc.pop("_id", None)
        tasks.append(DeveloperTask(**task_doc))
    
    return tasks


async def create_task(task: DeveloperTask) -> DeveloperTask:
    """Create a new task in MongoDB."""
    db = get_database()
    tasks_collection = db["tasks"]
    
    # Get next task_id
    max_task = await tasks_collection.find_one(sort=[("task_id", -1)])
    next_id = (max_task["task_id"] + 1) if max_task else 1
    
    task.task_id = next_id
    task_dict = task.model_dump()
    
    await tasks_collection.insert_one(task_dict)
    return task


async def get_task_by_id(task_id: int) -> Optional[DeveloperTask]:
    """Get a specific task by ID."""
    db = get_database()
    tasks_collection = db["tasks"]
    
    task_doc = await tasks_collection.find_one({"task_id": task_id})
    if task_doc:
        task_doc.pop("_id", None)
        return DeveloperTask(**task_doc)
    return None


async def seed_tasks() -> None:
    """Seed initial task data to MongoDB."""
    db = get_database()
    tasks_collection = db["tasks"]
    
    # Check if tasks already exist
    existing_count = await tasks_collection.count_documents({})
    if existing_count > 0:
        return  # Don't seed if data already exists
    
    initial_tasks = [
        {
            "task_id": 1,
            "title": "Refactor legacy service",
            "status": TaskStatus.COMPLETE.value,
            "hours_spent": 8.5
        },
        {
            "task_id": 2,
            "title": "Implement new user auth flow",
            "status": TaskStatus.IN_PROGRESS.value,
            "hours_spent": 15.0
        },
        {
            "task_id": 3,
            "title": "Write unit tests for checkout",
            "status": TaskStatus.PENDING.value,
            "hours_spent": 0.0
        }
    ]
    
    await tasks_collection.insert_many(initial_tasks)
