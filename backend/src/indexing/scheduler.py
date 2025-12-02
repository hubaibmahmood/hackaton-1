"""Daily indexing scheduler for cron jobs."""
import asyncio
import logging
from datetime import datetime, timezone

from src.config import settings, setup_logging
from src.database.postgres import postgres_db
from src.indexing.indexer import indexer

logger = logging.getLogger(__name__)

async def cleanup_sessions():
    """Cleanup expired sessions from the database."""
    try:
        query = """
            DELETE FROM sessions 
            WHERE expires_at < $1
        """
        now = datetime.now(timezone.utc)
        # We'll use postgres_db directly for this maintenance task
        # Assuming postgres_db exposes a way to get a connection or execute
        # If not, we might need to import the pool directly or add a method
        # For now, let's assume we can get a connection from the pool manager
        pool = await postgres_db.get_pool()
        if pool:
            async with pool.acquire() as conn:
                result = await conn.execute(query, now)
                logger.info(f"Cleaned up expired sessions. Rows affected: {result}")
        else:
            logger.error("Failed to connect to database for session cleanup")
    except Exception as e:
        logger.error(f"Session cleanup failed: {e}")

async def run_daily_tasks():
    """Execute daily maintenance tasks."""
    setup_logging()
    logger.info("Starting daily maintenance tasks...")
    
    # 1. Session Cleanup
    logger.info("Task 1/2: Session Cleanup")
    await cleanup_sessions()
    
    # 2. Indexing
    logger.info("Task 2/2: Content Indexing")
    try:
        # We assume the script is run from the project root or backend root
        # The Render configuration sets the working directory context
        import os
        # Try to locate book/docs relative to backend/ or project root
        docs_path = os.path.abspath("../book/docs") # If running from backend/
        if not os.path.exists(docs_path):
             docs_path = os.path.abspath("book/docs") # If running from project root
        
        if os.path.exists(docs_path):
             logger.info(f"Indexing directory: {docs_path}")
             await indexer.index_directory(docs_path)
        else:
             logger.warning(f"Docs directory not found at {docs_path}, skipping indexing")
    except Exception as e:
        logger.error(f"Indexing task failed: {e}")
        
    logger.info("Daily tasks completed.")

def main():
    """Entry point for cron job."""
    asyncio.run(run_daily_tasks())

if __name__ == "__main__":
    main()
