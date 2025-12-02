"""Error handling and logging middleware for FastAPI."""
import logging
import time
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors and providing friendly error messages."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle errors.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response
        """
        start_time = time.time()

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log successful requests
            logger.info(
                f"{request.method} {request.url.path} "
                f"completed in {process_time:.3f}s with status {response.status_code}"
            )

            return response

        except Exception as e:
            process_time = time.time() - start_time

            # Log error with context
            logger.error(
                f"{request.method} {request.url.path} "
                f"failed after {process_time:.3f}s: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )

            # Return friendly error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "An error occurred while processing your request",
                    "message": "Please try again. If the problem persists, contact support.",
                    "type": type(e).__name__,
                },
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging request details."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request details.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response
        """
        # Log incoming request (avoid logging sensitive data)
        logger.info(
            f"Incoming request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        response = await call_next(request)

        return response
