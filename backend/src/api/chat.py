"""Chat API endpoints for RAG chatbot."""
import logging
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Response, Cookie, status
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from src.models.query import ChatRequest, ChatResponse
from src.services.session_service import session_service, RateLimitExceeded
from src.agents.rag_agent import rag_agent
from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    response: Response,
    session_id: Optional[str] = Cookie(None),
) -> ChatResponse:
    """Chat endpoint for sending messages to the RAG chatbot.

    Args:
        request: Chat request with user message
        response: FastAPI response object (for setting cookies)
        session_id: Session ID from cookie (optional)

    Returns:
        ChatResponse with assistant message and citations

    Raises:
        HTTPException: Various HTTP errors for validation, rate limiting, etc.
    """
    try:
        # Get or create session
        if session_id:
            try:
                sess_uuid = UUID(session_id)
                is_valid = await session_service.validate_session(sess_uuid)

                if not is_valid:
                    # Create new session if invalid/expired
                    session = await session_service.create_session()
                    sess_uuid = session.session_id
                else:
                    sess_uuid = sess_uuid

            except (ValueError, ValidationError):
                # Invalid UUID format, create new session
                session = await session_service.create_session()
                sess_uuid = session.session_id
        else:
            # No session cookie, create new
            session = await session_service.create_session()
            sess_uuid = session.session_id

        # Set session cookie
        response.set_cookie(
            key="session_id",
            value=str(sess_uuid),
            max_age=int(settings.session_expiry_hours * 3600),
            httponly=True,
            secure=True,  # HTTPS only in production
            samesite="lax",
        )

        # Check rate limit
        try:
            await session_service.check_rate_limit(sess_uuid)
        except RateLimitExceeded as e:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(e),
            )

        # Persist user message
        await session_service.persist_message(
            session_id=sess_uuid,
            role="user",
            content=request.message,
        )

        # Get conversation history for context
        conversation_history = await session_service.retrieve_history(
            session_id=sess_uuid,
            max_messages=10,
        )

        # Run RAG agent
        result = await rag_agent.run(
            user_message=request.message,
            session_id=str(sess_uuid),
            conversation_history=conversation_history,
        )

        # Persist assistant message
        await session_service.persist_message(
            session_id=sess_uuid,
            role="assistant",
            content=result["answer"],
            citations=result.get("citations", []),
        )

        # Return response
        from datetime import datetime
        return ChatResponse(
            message=result["answer"],
            citations=result.get("citations", []),
            session_id=str(sess_uuid),
            timestamp=datetime.utcnow().isoformat(),
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again.",
        )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    response: Response,
    session_id: Optional[str] = Cookie(None),
) -> StreamingResponse:
    """Chat endpoint with Server-Sent Events streaming.

    Args:
        request: Chat request with user message
        response: FastAPI response object (for setting cookies)
        session_id: Session ID from cookie (optional)

    Returns:
        StreamingResponse with SSE events

    Raises:
        HTTPException: Various HTTP errors for validation, rate limiting, etc.
    """
    try:
        # Get or create session (same logic as above)
        if session_id:
            try:
                sess_uuid = UUID(session_id)
                is_valid = await session_service.validate_session(sess_uuid)

                if not is_valid:
                    session = await session_service.create_session()
                    sess_uuid = session.session_id
            except (ValueError, ValidationError):
                session = await session_service.create_session()
                sess_uuid = session.session_id
        else:
            session = await session_service.create_session()
            sess_uuid = session.session_id

        # Check rate limit
        try:
            await session_service.check_rate_limit(sess_uuid)
        except RateLimitExceeded as e:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(e),
            )

        # Persist user message
        await session_service.persist_message(
            session_id=sess_uuid,
            role="user",
            content=request.message,
        )

        # Get conversation history
        conversation_history = await session_service.retrieve_history(
            session_id=sess_uuid,
            max_messages=10,
        )

        # Stream generator
        async def event_stream():
            """Generate Server-Sent Events stream."""
            import json

            try:
                # Send session ID first
                yield f"data: {json.dumps({'type': 'session', 'session_id': str(sess_uuid)})}\n\n"

                # Run streaming agent
                async for event in rag_agent.run_streaming(
                    user_message=request.message,
                    session_id=str(sess_uuid),
                    conversation_history=conversation_history,
                ):
                    yield f"data: {json.dumps(event)}\n\n"

                    # If done, persist assistant message
                    if event.get("type") == "done":
                        await session_service.persist_message(
                            session_id=sess_uuid,
                            role="assistant",
                            content=event.get("full_content", ""),
                            citations=event.get("citations", []),
                        )

            except Exception as e:
                logger.error(f"Streaming error: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
                "Set-Cookie": f"session_id={str(sess_uuid)}; Max-Age={int(settings.session_expiry_hours * 3600)}; HttpOnly; Secure; SameSite=Lax",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat stream endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request.",
        )
