"""Unit tests for RAG agent."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from src.agents.rag_agent import RAGAgent

@pytest.fixture
def mock_runner():
    with patch("src.agents.rag_agent.Runner") as mock:
        yield mock

@pytest.fixture
def rag_agent(mock_runner):
    return RAGAgent()

@pytest.mark.asyncio
async def test_run_agent_success(rag_agent, mock_runner):
    # Mock Runner.run result
    mock_result = MagicMock()
    mock_result.final_output = "Test answer"
    mock_result.items = [] # No tool calls for simplicity
    
    mock_runner.run = AsyncMock(return_value=mock_result)
    
    result = await rag_agent.run(
        user_message="test query",
        session_id="test-session"
    )
    
    assert result["answer"] == "Test answer"
    assert result["session_id"] == "test-session"
    mock_runner.run.assert_called_once()

from openai.types.responses import ResponseTextDeltaEvent

@pytest.mark.asyncio
async def test_run_streaming_success(rag_agent, mock_runner):
    # Mock Runner.run_streamed result
    mock_result = MagicMock()
    
    # Mock stream_events async generator
    async def mock_stream():
        # Mock a text delta event
        mock_event = MagicMock()
        mock_event.type = "raw_response_event"
        
        # Mock the data structure for ResponseTextDeltaEvent
        # We need to mock isinstance(event.data, ResponseTextDeltaEvent) to be True
        # Since we can't easily mock isinstance for a specific class without creating an instance,
        # we'll construct a real ResponseTextDeltaEvent or mock the check.
        # Constructing real Pydantic model is safer if possible, but let's patch the check logic in source
        # Or better, make the mock look like it.
        
        mock_data = MagicMock(spec=ResponseTextDeltaEvent)
        mock_data.delta = "Test delta"
        mock_event.data = mock_data
        
        yield mock_event
        
    mock_result.stream_events = mock_stream
    
    # run_streamed is synchronous in the SDK now, but returns an object with async stream_events
    mock_runner.run_streamed.return_value = mock_result
    
    events = []
    async for event in rag_agent.run_streaming("test", "session"):
        events.append(event)
    
    assert len(events) > 0
    # Check for content event
    content_events = [e for e in events if e.get("type") == "content"]
    assert len(content_events) == 1
    assert content_events[0]["content"] == "Test delta"
