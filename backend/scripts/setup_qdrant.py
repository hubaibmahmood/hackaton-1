"""Setup Qdrant collection for the RAG chatbot."""
import asyncio
import logging

from src.config import setup_logging
from src.database.qdrant import qdrant_db

logger = logging.getLogger(__name__)


async def main():
    """Create Qdrant collection and verify with test vector."""
    setup_logging()
    logger.info("Setting up Qdrant collection...")

    # Create collection
    success = await qdrant_db.create_collection()
    if not success:
        logger.error("Failed to create collection")
        return

    # Verify with test vector
    success = await qdrant_db.insert_test_vector()
    if not success:
        logger.error("Failed to insert test vector")
        return

    logger.info("✅ Qdrant collection setup complete!")


if __name__ == "__main__":
    asyncio.run(main())
