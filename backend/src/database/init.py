"""
Database initialization with connection pooling for Neon PostgreSQL.
Extends existing postgres.py with pool management for auth operations.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row

from src.config import settings

logger = logging.getLogger(__name__)

# Global connection pool instance
_connection_pool: AsyncConnectionPool | None = None


async def init_db_pool(
    min_size: int = 1,
    max_size: int = 10,
    timeout: float = 30.0
) -> AsyncConnectionPool:
    """
    Initialize database connection pool for auth operations.

    Args:
        min_size: Minimum number of connections in pool
        max_size: Maximum number of connections in pool
        timeout: Connection timeout in seconds

    Returns:
        AsyncConnectionPool: Initialized connection pool
    """
    global _connection_pool

    if _connection_pool is not None:
        logger.warning("Connection pool already initialized")
        return _connection_pool

    logger.info(f"Initializing database connection pool (min={min_size}, max={max_size})")

    _connection_pool = AsyncConnectionPool(
        conninfo=settings.neon_db_url,
        min_size=min_size,
        max_size=max_size,
        timeout=timeout,
        kwargs={"row_factory": dict_row},
        open=False  # Don't open immediately, call open() explicitly
    )

    await _connection_pool.open()
    logger.info("Database connection pool opened")

    return _connection_pool


async def close_db_pool() -> None:
    """Close the database connection pool gracefully."""
    global _connection_pool

    if _connection_pool is not None:
        logger.info("Closing database connection pool")
        await _connection_pool.close()
        _connection_pool = None
        logger.info("Database connection pool closed")


@asynccontextmanager
async def get_db_connection() -> AsyncGenerator:
    """
    Get a database connection from the pool.

    Usage:
        async with get_db_connection() as conn:
            await conn.execute("SELECT * FROM users")

    Yields:
        Connection from the pool with dict_row factory
    """
    if _connection_pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")

    async with _connection_pool.connection() as conn:
        yield conn


async def health_check() -> bool:
    """
    Check if database connection pool is healthy.

    Returns:
        bool: True if database is accessible, False otherwise
    """
    try:
        async with get_db_connection() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database pool health check failed: {e}")
        return False
