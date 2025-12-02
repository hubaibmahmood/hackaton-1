"""
Structured logging utility with correlation IDs for FastAPI backend.
Provides consistent log format across the API server.
"""
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4


class StructuredLogger:
    """Structured logger with JSON output and correlation IDs."""

    def __init__(self, name: str = "api-server"):
        self.name = name
        self.context: Dict[str, Any] = {}
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Setup Python logger with custom formatter."""
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)

        # Remove existing handlers
        self.logger.handlers = []

        # Console handler with JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

        # Prevent propagation to root logger
        self.logger.propagate = False

    def _format_log(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format log entry as JSON."""
        log_entry = {
            "level": level,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": self.name,
            "message": message,
            "correlationId": self.context.get("correlationId", "no-correlation-id"),
            **self.context,
            **(context or {}),
        }
        return json.dumps(log_entry)

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set global context for all subsequent logs."""
        self.context.update(context)

    def clear_context(self) -> None:
        """Clear global context."""
        self.context = {}

    @staticmethod
    def generate_correlation_id() -> str:
        """Generate a new correlation ID."""
        return str(uuid4())

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message."""
        self.logger.debug(self._format_log("debug", message, context))

    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log info message."""
        self.logger.info(self._format_log("info", message, context))

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message."""
        self.logger.warning(self._format_log("warning", message, context))

    def error(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log error message."""
        self.logger.error(self._format_log("error", message, context))

    def child(self, context: Dict[str, Any]) -> "StructuredLogger":
        """Create child logger with inherited context."""
        child = StructuredLogger(self.name)
        child.context = {**self.context, **context}
        return child


# Global logger instance
logger = StructuredLogger("api-server")


__all__ = ["logger", "StructuredLogger"]
