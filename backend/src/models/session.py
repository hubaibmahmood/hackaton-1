"""Session models for conversation management."""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.config import settings


class ConversationMessage(BaseModel):
    """Single message in conversation history."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    citations: Optional[list[dict]] = Field(None, description="Citations (for assistant messages)")


class UserSession(BaseModel):
    """User session model for conversation state."""

    session_id: UUID = Field(default_factory=uuid4, description="Unique session identifier")
    conversation_history: list[ConversationMessage] = Field(
        default_factory=list,
        description="Full conversation history"
    )

    # Rate limiting
    rate_limit_counter: int = Field(default=0, description="Number of queries in current window")
    rate_limit_window_start: datetime = Field(
        default_factory=datetime.utcnow,
        description="Start of rate limit window"
    )

    # Session lifecycle
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(hours=settings.session_expiry_hours),
        description="Session expiration timestamp"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation time")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity timestamp")

    # Optional metadata (no PII)
    current_page_url: Optional[str] = Field(None, description="Current page URL")
    user_agent: Optional[str] = Field(None, description="User agent string")

    def is_expired(self) -> bool:
        """Check if session has expired.

        Returns:
            bool: True if session is expired
        """
        return datetime.utcnow() > self.expires_at

    def add_message(self, role: str, content: str, citations: Optional[list[dict]] = None) -> None:
        """Add message to conversation history.

        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
            citations: Optional citations for assistant messages
        """
        message = ConversationMessage(
            role=role,
            content=content,
            citations=citations,
        )
        self.conversation_history.append(message)
        self.last_activity = datetime.utcnow()

    def get_conversation_context(self, max_messages: int = 10) -> list[dict]:
        """Get recent conversation history for context.

        Args:
            max_messages: Maximum number of messages to return

        Returns:
            List of message dictionaries for OpenAI API
        """
        recent_messages = self.conversation_history[-max_messages:]
        return [
            {"role": msg.role, "content": msg.content}
            for msg in recent_messages
        ]
