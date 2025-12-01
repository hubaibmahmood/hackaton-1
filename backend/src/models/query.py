"""Query and Response models for chatbot interactions."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Query(BaseModel):
    """User query model."""

    question: str = Field(..., description="User's question text", min_length=1, max_length=2000)
    session_id: Optional[UUID] = Field(None, description="Session identifier for conversation context")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Query timestamp")

    # Page context (will be used in User Story 3)
    current_page_url: Optional[str] = Field(None, description="Current page URL for context")
    page_metadata: Optional[dict] = Field(None, description="Page metadata (part, chapter, section)")

    # Text selection context (will be used in User Story 2)
    selected_text: Optional[str] = Field(None, description="Text selected by user")
    selection_metadata: Optional[dict] = Field(None, description="Selection location metadata")


class Response(BaseModel):
    """Chatbot response model."""

    answer: str = Field(..., description="Generated answer text")
    citations: list[dict] = Field(default_factory=list, description="List of source citations")
    confidence_score: Optional[float] = Field(None, description="Confidence score (0-1)", ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    session_id: UUID = Field(..., description="Session identifier")


class ChatRequest(BaseModel):
    """Chat API request model."""

    message: str = Field(..., description="User message", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="Session ID (will be created if not provided)")

    # Optional context fields
    selected_text: Optional[str] = Field(None, description="Selected text for context")
    current_page_url: Optional[str] = Field(None, description="Current page URL")


class ChatResponse(BaseModel):
    """Chat API response model."""

    message: str = Field(..., description="Assistant response message")
    citations: list[dict] = Field(default_factory=list, description="Source citations")
    session_id: str = Field(..., description="Session identifier")
    timestamp: str = Field(..., description="Response timestamp (ISO format)")
