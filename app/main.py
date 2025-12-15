from typing import Dict, List
import asyncio
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.models import DeveloperTask, ProductivityReport, TaskStatus, TaskLogResponse, Token, User, Role
from app.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.dependencies import get_current_active_user, PermissionChecker
from app.rbac import ROLES, get_user_permissions
from app.responses import PROTECTED_RESPONSES, AUTHENTICATION_RESPONSES
from app.routers import ProtectedAPIRouter


# --- Mock Database / In-Memory Service Logic
MOCK_TASKS: Dict[int, DeveloperTask] = {
    1: DeveloperTask(task_id=1, title="Refactor legacy service", status=TaskStatus.COMPLETE, hours_spent=8.5),
    2: DeveloperTask(task_id=2, title="Implement new user auth flow", status=TaskStatus.IN_PROGRESS, hours_spent=15.0),
    3: DeveloperTask(task_id=3, title="Write unit tests for checkout", status=TaskStatus.PENDING, hours_spent=0.0),
}

# Simulate asynchronous I/O with a slight delay
async def fetch_all_tasks() -> List[DeveloperTask]:
    """Simulates fetching all tasks asynchronously."""
    await asyncio.sleep(0.01)
    return list(MOCK_TASKS.values())

async def generate_productivity_report() -> ProductivityReport:
    """Calculates key metrics based on all tasks."""
    tasks = await fetch_all_tasks()
    
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.status == TaskStatus.COMPLETE)
    
    total_hours_spent = sum(task.hours_spent for task in tasks)
    completion_rate = round(completed_tasks / total_tasks, 2) if total_tasks > 0 else 0.0
    
    return ProductivityReport(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        total_hours_spent=round(total_hours_spent, 2),
        completion_rate=completion_rate
    )


# --- FastAPI Initialization and Routes ---
app = FastAPI(title="Productivity Reporting System")

# Create protected router with automatic RBAC
protected_router = ProtectedAPIRouter(tags=["protected"])


@app.post("/token", response_model=Token, responses=AUTHENTICATION_RESPONSES)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    OAuth2 compatible token login endpoint.
    FastAPI automatically creates the login form in /docs.
    
    Test credentials:
    - username: nicolas.schmid
    - password: secret
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@app.get("/status")
async def get_status() -> Dict[str, str]:
    return {"status": "ok"}


@protected_router.get("/users/me", ["user:view"], response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
    """Returns the currently authenticated user."""
    return current_user


@protected_router.get("/users/me/permissions", ["user:view"], response_model=List[str])
async def read_user_permissions(current_user: User = Depends(get_current_active_user)) -> List[str]:
    """Returns all permissions for the current user."""
    return sorted(list(get_user_permissions(current_user)))


@protected_router.get("/roles", ["user:view"], response_model=List[Role])
async def get_all_roles() -> List[Role]:
    """Returns all available roles and their permissions."""
    return list(ROLES.values())


@protected_router.get("/tasks", ["task:view"], response_model=List[DeveloperTask])
async def get_all_tasks() -> List[DeveloperTask]:
    """Returns a list of all logged tasks. (Protected - requires task:view)"""
    return await fetch_all_tasks()


@protected_router.get("/report", ["report:view"], response_model=ProductivityReport)
async def get_productivity_report() -> ProductivityReport:
    """Returns the calculated productivity report. (Protected - requires report:view)"""
    return await generate_productivity_report()


@protected_router.post("/log_task", ["task:create"], response_model=TaskLogResponse)
async def log_task(task: DeveloperTask) -> TaskLogResponse:
    """Logs a new task. (Protected - requires task:create)"""
    new_id = max(MOCK_TASKS.keys()) + 1 if MOCK_TASKS else 1
    task.task_id = new_id
    MOCK_TASKS[new_id] = task
    
    return TaskLogResponse(
        task_id=task.task_id,
        message=f"Task ID {task.task_id} logged successfully."
    )


# Include the protected router
app.include_router(protected_router)
