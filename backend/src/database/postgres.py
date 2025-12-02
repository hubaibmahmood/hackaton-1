"""Neon Postgres database connection using psycopg (async)."""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import psycopg
from psycopg import AsyncConnection
from psycopg.rows import dict_row

from src.config import settings

logger = logging.getLogger(__name__)


class PostgresDB:
    """Neon Postgres database connection manager."""

    def __init__(self) -> None:
        """Initialize database connection manager."""
        self.connection_string = settings.neon_db_url
        self._connection: AsyncConnection | None = None

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[AsyncConnection, None]:
        """Get a database connection from the pool.

        Yields:
            AsyncConnection: Database connection with dict_row factory
        """
        async with await psycopg.AsyncConnection.connect(
            self.connection_string,
            row_factory=dict_row,
        ) as conn:
            yield conn

    async def health_check(self) -> bool:
        """Check if database connection is healthy.

        Returns:
            bool: True if database is accessible, False otherwise
        """
        try:
            async with self.get_connection() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database instance
postgres_db = PostgresDB()
