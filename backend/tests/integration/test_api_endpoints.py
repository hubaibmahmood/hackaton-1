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

def test_chat_endpoint_with_selection(mock_rag_agent, mock_session_service):
    # Mock agent response
    mock_rag_agent.run = AsyncMock(return_value={
        "answer": "Answer about selection",
        "citations": [],
        "session_id": "test-uuid"
    })

    response = client.post(
        "/api/chat/",
        json={
            "message": "Explain this",
            "selected_text": "LIDAR works by emitting laser pulses.",
            "current_page_url": "/docs/chapter-2"
        },
        headers={"Cookie": "session_id=test-uuid"}
    )

    assert response.status_code == 200
    
    # Verify agent called with selection arguments
    mock_rag_agent.run.assert_called_once()
    call_kwargs = mock_rag_agent.run.call_args[1]
    assert call_kwargs["user_message"] == "Explain this"
    assert call_kwargs["selected_text"] == "LIDAR works by emitting laser pulses."
    assert call_kwargs["current_page_url"] == "/docs/chapter-2"

def test_chat_endpoint_contextual(mock_rag_agent, mock_session_service):
    # Mock agent response to simulate contextual advice
    mock_rag_agent.run = AsyncMock(return_value={
        "answer": "Based on your location in Chapter 3, you should review Chapters 1 and 2.",
        "citations": [],
        "session_id": "test-uuid"
    })

    response = client.post(
        "/api/chat/",
        json={
            "message": "What are prerequisites?",
            "current_page_url": "/docs/part-01/chapter-03"
        },
        headers={"Cookie": "session_id=test-uuid"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "Chapters 1 and 2" in data["message"]
    
    # Verify agent called with page context
    mock_rag_agent.run.assert_called_once()
    call_kwargs = mock_rag_agent.run.call_args[1]
    assert call_kwargs["current_page_url"] == "/docs/part-01/chapter-03"

def test_chat_endpoint_discovery(mock_rag_agent, mock_session_service):
    # Mock agent response for discovery query
    mock_rag_agent.run = AsyncMock(return_value={
        "answer": "Obstacle avoidance is discussed in Chapter 2 (LIDAR) and Chapter 4 (Navigation).",
        "citations": [
            {"text": "Chapter 2 > LIDAR", "url": "/docs/ch2#lidar"},
            {"text": "Chapter 4 > Navigation", "url": "/docs/ch4#nav"}
        ],
        "session_id": "test-uuid"
    })

    response = client.post(
        "/api/chat/",
        json={"message": "Where is obstacle avoidance discussed?"},
        headers={"Cookie": "session_id=test-uuid"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["citations"]) == 2
    assert "Obstacle avoidance" in data["message"]
    
    # Verify agent run called
    mock_rag_agent.run.assert_called_once()