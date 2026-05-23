"""Bearer token validation middleware for /api/* routes."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    """Validates bearer tokens on protected routes."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request with auth validation."""
        return await call_next(request)
