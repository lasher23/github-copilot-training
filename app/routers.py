"""Custom router with automatic RBAC permission checking."""
from typing import Any, Callable, List, TypeVar, overload
from functools import wraps
from fastapi import APIRouter, Depends
from app.dependencies import PermissionChecker
from app.responses import PROTECTED_RESPONSES


class ProtectedAPIRouter(APIRouter):
    """
    Custom APIRouter that automatically applies permission checks and response docs.
    
    Usage:
        router = ProtectedAPIRouter()
        
        @router.get("/tasks", ["task:view"])
        async def get_tasks(current_user): 
            return tasks
        
        # Router automatically injects PermissionChecker dependency
        # and adds 401/403 responses to OpenAPI docs
    """
    
    def __init__(self, **kwargs: Any):
        # Apply default responses to all routes
        default_responses = kwargs.pop("responses", {})
        default_responses.update(PROTECTED_RESPONSES)
        super().__init__(responses=default_responses, **kwargs)
    
    def _create_protected_endpoint(
        self, 
        method: str, 
        path: str, 
        permissions: List[str],
        **kwargs: Any
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Helper to create protected endpoints with permission checking."""
        # Merge any additional responses with default protected responses
        endpoint_responses = kwargs.pop("responses", {})
        merged_responses = {**PROTECTED_RESPONSES, **endpoint_responses}
        
        # Get the original route method
        route_method = getattr(super(), method.lower())
        
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            # Add PermissionChecker as a dependency if not already present
            dependencies = kwargs.get("dependencies", [])
            dependencies.append(Depends(PermissionChecker(permissions)))
            kwargs["dependencies"] = dependencies
            
            # Register the route with merged responses
            registered_route = route_method(path, responses=merged_responses, **kwargs)(func)
            return registered_route  # type: ignore[no-any-return]
        
        return decorator
    
    def get(self, path: str, permissions: List[str], **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:  # type: ignore[override]
        """GET endpoint with automatic permission checking."""
        return self._create_protected_endpoint("GET", path, permissions, **kwargs)
    
    def post(self, path: str, permissions: List[str], **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:  # type: ignore[override]
        """POST endpoint with automatic permission checking."""
        return self._create_protected_endpoint("POST", path, permissions, **kwargs)
    
    def put(self, path: str, permissions: List[str], **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:  # type: ignore[override]
        """PUT endpoint with automatic permission checking."""
        return self._create_protected_endpoint("PUT", path, permissions, **kwargs)
    
    def delete(self, path: str, permissions: List[str], **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:  # type: ignore[override]
        """DELETE endpoint with automatic permission checking."""
        return self._create_protected_endpoint("DELETE", path, permissions, **kwargs)
    
    def patch(self, path: str, permissions: List[str], **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:  # type: ignore[override]
        """PATCH endpoint with automatic permission checking."""
        return self._create_protected_endpoint("PATCH", path, permissions, **kwargs)
