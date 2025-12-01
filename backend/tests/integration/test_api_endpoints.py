"""Integration tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

from src.main import app
from src.services.session_service import session_service

client = TestClient(app)

@pytest.fixture
def mock_rag_agent():
    with patch("src.api.chat.rag_agent") as mock:
        yield mock

@pytest.fixture
def mock_session_service():
    # We need to patch the global session_service used in api/chat.py
    with patch("src.api.chat.session_service", side_effect=session_service) as mock:
        # Setup default behaviors
        mock.create_session = AsyncMock()
        mock.validate_session = AsyncMock(return_value=True)
        mock.check_rate_limit = AsyncMock(return_value=True)
        mock.persist_message = AsyncMock()
        mock.retrieve_history = AsyncMock(return_value=[])
        
        # Setup create_session to return a session with ID
        mock_session = MagicMock()
        mock_session.session_id = "test-uuid"
        mock.create_session.return_value = mock_session
        
        yield mock

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok" or "degraded" # Depending on DB health

def test_chat_endpoint_success(mock_rag_agent, mock_session_service):
    # Mock agent response
    mock_rag_agent.run = AsyncMock(return_value={
        "answer": "Test Answer",
        "citations": [{"text": "citation", "url": "http://url"}],
        "session_id": "test-uuid"
    })

    response = client.post(
        "/api/chat/",
        json={"message": "Hello"},
        headers={"Cookie": "session_id=test-uuid"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Test Answer"
    assert len(data["citations"]) == 1
    assert data["session_id"] == "test-uuid"

def test_chat_endpoint_no_session(mock_rag_agent, mock_session_service):
    # Mock agent response
    mock_rag_agent.run = AsyncMock(return_value={
        "answer": "New Session Answer",
        "citations": [],
        "session_id": "new-uuid"
    })
    
    # Update session mock to return new ID
    mock_session_service.create_session.return_value.session_id = "new-uuid"

    response = client.post(
        "/api/chat/",
        json={"message": "Start chat"}
    )

    assert response.status_code == 200
    assert "session_id" in response.cookies # Cookie should be set
    
def test_chat_endpoint_rate_limit(mock_rag_agent, mock_session_service):
    # Mock rate limit exception
    from src.services.session_service import RateLimitExceeded
    mock_session_service.check_rate_limit.side_effect = RateLimitExceeded("Rate limit exceeded")

    response = client.post(
        "/api/chat/",
        json={"message": "Spam"},
        headers={"Cookie": "session_id=test-uuid"}
    )

    assert response.status_code == 429
