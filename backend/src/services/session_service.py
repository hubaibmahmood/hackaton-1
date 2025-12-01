"""Session service for conversation history and rate limiting."""
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

from src.config import settings
from src.database.postgres import postgres_db
from src.models.session import UserSession, ConversationMessage

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Raised when session rate limit is exceeded."""
    pass


class SessionService:
    """Service for managing user sessions."""

    async def create_session(
        self,
        session_id: Optional[UUID] = None,
        user_agent: Optional[str] = None,
    ) -> UserSession:
        """Create a new session.

        Args:
            session_id: Optional session ID (generates new if not provided)
            user_agent: Optional user agent string

        Returns:
            Created UserSession
        """
        if session_id is None:
            session_id = uuid4()

        session = UserSession(
            session_id=session_id,
            user_agent=user_agent,
        )

        # Insert into database
        async with postgres_db.get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO sessions (
                    session_id,
                    conversation_history,
                    rate_limit_counter,
                    rate_limit_window_start,
                    expires_at,
                    created_at,
                    last_activity,
                    user_agent
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(session.session_id),
                    json.dumps([]),  # Empty JSONB array
                    session.rate_limit_counter,
                    session.rate_limit_window_start,
                    session.expires_at,
                    session.created_at,
                    session.last_activity,
                    session.user_agent,
                ),
            )

        logger.info(f"Created session: {session_id}")
        return session

    async def load_session(self, session_id: UUID) -> Optional[UserSession]:
        """Load session from database.

        Args:
            session_id: Session identifier

        Returns:
            UserSession if found, None otherwise
        """
        async with postgres_db.get_connection() as conn:
            result = await conn.execute(
                """
                SELECT
                    session_id,
                    conversation_history,
                    rate_limit_counter,
                    rate_limit_window_start,
                    expires_at,
                    created_at,
                    last_activity,
                    current_page_url,
                    user_agent
                FROM sessions
                WHERE session_id = %s
                """,
                (str(session_id),),
            )
            row = await result.fetchone()

        if not row:
            logger.warning(f"Session not found: {session_id}")
            return None

        # Convert JSONB to ConversationMessage objects
        conversation_history = [
            ConversationMessage(**msg) for msg in (row["conversation_history"] or [])
        ]

        # Handle session_id - might already be UUID from Postgres
        session_id = row["session_id"]
        if isinstance(session_id, str):
            session_id = UUID(session_id)

        session = UserSession(
            session_id=session_id,
            conversation_history=conversation_history,
            rate_limit_counter=row["rate_limit_counter"],
            rate_limit_window_start=row["rate_limit_window_start"],
            expires_at=row["expires_at"],
            created_at=row["created_at"],
            last_activity=row["last_activity"],
            current_page_url=row["current_page_url"],
            user_agent=row["user_agent"],
        )

        return session

    async def validate_session(self, session_id: UUID) -> bool:
        """Validate session exists and is not expired.

        Args:
            session_id: Session identifier

        Returns:
            True if valid, False otherwise
        """
        session = await self.load_session(session_id)
        if not session:
            return False

        if session.is_expired():
            logger.warning(f"Session expired: {session_id}")
            return False

        return True

    async def persist_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        citations: Optional[list[dict]] = None,
    ) -> None:
        """Persist message to conversation history.

        Args:
            session_id: Session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            citations: Optional citations for assistant messages
        """
        message = ConversationMessage(
            role=role,
            content=content,
            citations=citations,
        )

        # Serialize to JSON with datetime handling
        message_dict = message.model_dump(mode='json')

        async with postgres_db.get_connection() as conn:
            await conn.execute(
                """
                UPDATE sessions
                SET
                    conversation_history = conversation_history || %s::jsonb,
                    last_activity = %s
                WHERE session_id = %s
                """,
                (
                    json.dumps([message_dict]),  # Serialize to JSON string
                    datetime.now(timezone.utc),
                    str(session_id),
                ),
            )

        logger.debug(f"Persisted message to session {session_id}: {role}")

    async def retrieve_history(
        self,
        session_id: UUID,
        max_messages: int = 10,
    ) -> list[dict]:
        """Retrieve conversation history for context.

        Args:
            session_id: Session identifier
            max_messages: Maximum number of messages to return

        Returns:
            List of message dictionaries for OpenAI API
        """
        session = await self.load_session(session_id)
        if not session:
            return []

        return session.get_conversation_context(max_messages)

    async def check_rate_limit(self, session_id: UUID) -> bool:
        """Check if session is within rate limit.

        Args:
            session_id: Session identifier

        Returns:
            True if within limit

        Raises:
            RateLimitExceeded: If rate limit exceeded
        """
        session = await self.load_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        now = datetime.now(timezone.utc)
        window_duration = timedelta(minutes=1)
        window_start = now - window_duration

        # Reset counter if outside window
        if session.rate_limit_window_start < window_start:
            # Reset window
            async with postgres_db.get_connection() as conn:
                await conn.execute(
                    """
                    UPDATE sessions
                    SET
                        rate_limit_counter = 0,
                        rate_limit_window_start = %s
                    WHERE session_id = %s
                    """,
                    (now, str(session_id)),
                )
            session.rate_limit_counter = 0
            session.rate_limit_window_start = now

        # Check limit
        if session.rate_limit_counter >= settings.rate_limit_queries_per_minute:
            logger.warning(f"Rate limit exceeded for session {session_id}")
            raise RateLimitExceeded(
                f"Rate limit exceeded. Maximum {settings.rate_limit_queries_per_minute} queries per minute."
            )

        # Increment counter
        async with postgres_db.get_connection() as conn:
            await conn.execute(
                """
                UPDATE sessions
                SET
                    rate_limit_counter = rate_limit_counter + 1,
                    last_activity = %s
                WHERE session_id = %s
                """,
                (now, str(session_id)),
            )

        return True


# Global session service instance
session_service = SessionService()
