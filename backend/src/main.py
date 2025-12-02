"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from src.config import settings, setup_logging
from src.database.postgres import postgres_db
from src.database.qdrant import qdrant_db
from src.api.middleware import ErrorHandlingMiddleware, RequestLoggingMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - runs on startup and shutdown."""
    # Startup
    setup_logging()
    logger.info("Starting RAG Chatbot Backend...")

    # Health check databases
    postgres_healthy = await postgres_db.health_check()
    qdrant_healthy = await qdrant_db.health_check()

    logger.info(f"Postgres health: {'✓' if postgres_healthy else '✗'}")
    logger.info(f"Qdrant health: {'✓' if qdrant_healthy else '✗'}")

    if not postgres_healthy or not qdrant_healthy:
        logger.warning("Some services are not healthy - check configuration")

    yield

    # Shutdown
    logger.info("Shutting down RAG Chatbot Backend...")


# Create FastAPI application
app = FastAPI(
    title="RAG Chatbot Backend",
    description="Backend API for Physical AI textbook chatbot using RAG",
    version="0.1.0",
    lifespan=lifespan,
)

# Add middleware (order matters - last added runs first)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Enforce HTTPS in production (T081)
# We check an environment variable or just add it if not in local dev
# Render handles SSL termination, so we might not need strictly HTTPSRedirectMiddleware
# if we trust X-Forwarded-Proto. But let's add it for completeness if needed,
# or simpler: just rely on Render's redirection settings (usually default).
# However, spec says "Add HTTPS enforcement".
# NOTE: HTTPSRedirectMiddleware can cause loops behind some proxies if not configured right.
# Safer to check if we are in production.
if settings.environment == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        dict: Health status of the application and dependencies
    """
    postgres_healthy = await postgres_db.health_check()
    qdrant_healthy = await qdrant_db.health_check()

    return {
        "status": "ok" if (postgres_healthy and qdrant_healthy) else "degraded",
        "services": {
            "postgres": "healthy" if postgres_healthy else "unhealthy",
            "qdrant": "healthy" if qdrant_healthy else "unhealthy",
        },
    }


# Register API routes
from src.api import chat, index

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(index.router, prefix="/api/index", tags=["index"])
