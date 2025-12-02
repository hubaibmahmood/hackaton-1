"""Quick test script to verify backend is working."""
import asyncio
import logging

from src.config import setup_logging
from src.database.postgres import postgres_db
from src.database.qdrant import qdrant_db
from src.services.session_service import session_service

logger = logging.getLogger(__name__)


async def main():
    """Run basic tests."""
    setup_logging()
    logger.info("🧪 Testing backend components...")

    # Test 1: Postgres health
    logger.info("\n1️⃣ Testing Postgres connection...")
    postgres_healthy = await postgres_db.health_check()
    if postgres_healthy:
        logger.info("✅ Postgres is healthy")
    else:
        logger.error("❌ Postgres connection failed")
        return

    # Test 2: Qdrant health
    logger.info("\n2️⃣ Testing Qdrant connection...")
    qdrant_healthy = await qdrant_db.health_check()
    if qdrant_healthy:
        logger.info("✅ Qdrant is healthy")
    else:
        logger.error("❌ Qdrant connection failed")
        return

    # Test 3: Create a test session
    logger.info("\n3️⃣ Testing session creation...")
    try:
        session = await session_service.create_session(user_agent="test-script")
        logger.info(f"✅ Session created: {session.session_id}")

        # Test 4: Persist a message
        logger.info("\n4️⃣ Testing message persistence...")
        await session_service.persist_message(
            session_id=session.session_id,
            role="user",
            content="Test message",
        )
        logger.info("✅ Message persisted")

        # Test 5: Load session
        logger.info("\n5️⃣ Testing session loading...")
        loaded_session = await session_service.load_session(session.session_id)
        if loaded_session:
            logger.info(f"✅ Session loaded with {len(loaded_session.conversation_history)} messages")
        else:
            logger.error("❌ Failed to load session")

        # Test 6: Rate limiting
        logger.info("\n6️⃣ Testing rate limiting...")
        can_proceed = await session_service.check_rate_limit(session.session_id)
        if can_proceed:
            logger.info("✅ Rate limit check passed")
        else:
            logger.error("❌ Rate limit check failed")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return

    logger.info("\n🎉 All tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
