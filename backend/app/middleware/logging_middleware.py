"""Structured JSON request logging middleware."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs requests in structured JSON format."""
    
    async def dispatch(self, request: Request, call_next):
        """Log request/response."""
        logger = structlog.get_logger()
        logger.info("request", method=request.method, path=request.url.path)
        response = await call_next(request)
        return response
