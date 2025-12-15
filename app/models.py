from enum import Enum
from pydantic import BaseModel
from typing import List


class TaskStatus(str, Enum):
    """Available statuses for any task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class DeveloperTask(BaseModel):
    """Model for a single task logged by a developer."""
    task_id: int
    title: str
    status: TaskStatus = TaskStatus.PENDING
    hours_spent: float = 0.0


class ProductivityReport(BaseModel):
    """The final calculated report."""
    total_tasks: int
    completed_tasks: int
    total_hours_spent: float
    completion_rate: float


class TaskLogResponse(BaseModel):
    """Response model for logging a new task."""
    task_id: int
    message: str


class Permission(BaseModel):
    """Individual permission following pattern: resource:action"""
    name: str  # e.g., "task:create", "task:view", "report:view"
    description: str | None = None


class Role(BaseModel):
    """Role containing multiple permissions"""
    name: str
    permissions: List[str]  # List of permission names
    description: str | None = None


class User(BaseModel):
    """Model for an authenticated user."""
    username: str
    email: str
    full_name: str | None = None
    disabled: bool = False
    roles: List[str] = []  # List of role names assigned to user


class UserInDB(User):
    """User model with hashed password for database storage."""
    hashed_password: str


class Token(BaseModel):
    """OAuth2 token response."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Data extracted from JWT token."""
    username: str | None = None
