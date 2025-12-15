"""Reusable OpenAPI response definitions for FastAPI endpoints."""
from typing import Any, Dict

PROTECTED_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    401: {
        "description": "Unauthorized - Invalid or missing authentication token",
        "content": {
            "application/json": {
                "example": {"detail": "Could not validate credentials"}
            }
        }
    },
    403: {
        "description": "Forbidden - Insufficient permissions",
        "content": {
            "application/json": {
                "example": {"detail": "Permission denied. Required permission: task:view"}
            }
        }
    },
}

AUTHENTICATION_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    401: {
        "description": "Unauthorized - Invalid credentials",
        "content": {
            "application/json": {
                "example": {"detail": "Incorrect username or password"}
            }
        }
    },
}
