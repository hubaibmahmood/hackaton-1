"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
from src.api import chat

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
# Index router will be added when indexing pipeline is complete
# from src.api import index
# app.include_router(index.router, prefix="/api/index", tags=["index"])
