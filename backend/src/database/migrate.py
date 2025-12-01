"""Database migration runner."""
import asyncio
import logging
from pathlib import Path

from src.config import setup_logging
from src.database.postgres import postgres_db

logger = logging.getLogger(__name__)


async def run_migrations() -> None:
    """Run all database migrations in order."""
    setup_logging()
    logger.info("Starting database migrations...")

    migrations_dir = Path(__file__).parent / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        logger.warning("No migration files found")
        return

    async with postgres_db.get_connection() as conn:
        for migration_file in migration_files:
            logger.info(f"Running migration: {migration_file.name}")
            try:
                sql = migration_file.read_text()
                await conn.execute(sql)
                logger.info(f"✓ Migration {migration_file.name} completed successfully")
            except Exception as e:
                logger.error(f"✗ Migration {migration_file.name} failed: {e}")
                raise

    logger.info("All migrations completed successfully")

    # Verify schema
    async with postgres_db.get_connection() as conn:
        result = await conn.execute(
            "SELECT * FROM sessions LIMIT 1"
        )
        logger.info("✓ Sessions table verified")


if __name__ == "__main__":
    asyncio.run(run_migrations())
