"""End-to-End RAG flow tests."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from src.agents.rag_agent import RAGAgent

@pytest.fixture
def mock_runner_e2e():
    # We want to mock the Runner but let the Agent logic work?
    # Actually, the Agent uses Runner to execute.
    # To test the "flow", we simulate the Runner calling the tool.
    
    with patch("src.agents.rag_agent.Runner") as mock:
        yield mock

@pytest.fixture
def mock_retrieval_service():
    with patch("src.agents.tools.retrieval_service") as mock:
        yield mock

@pytest.fixture
def rag_agent(mock_runner_e2e):
    return RAGAgent()

@pytest.mark.asyncio
async def test_rag_flow_with_citations(rag_agent, mock_runner_e2e):
    # Mock the result from the runner to simulate a successful RAG response
    # This verifies the agent processes the runner's output correctly
    
    mock_result = MagicMock()
    mock_result.final_output = "LIDAR is a sensor that uses laser light. According to Chapter 2, it measures distance."
    
    # Mock tool call item to verify citation extraction if we implement it later
    # Currently citation extraction is from answer text or explicit list if tool returned structured data
    # The current implementation extracts citations if they are in the tool calls?
    # The code says:
    # citations = []
    # if hasattr(result, 'items'): ...
    
    mock_tool_item = MagicMock()
    mock_tool_item.type = 'tool_call'
    mock_result.items = [mock_tool_item]
    
    mock_runner_e2e.run = AsyncMock(return_value=mock_result)
    
    result = await rag_agent.run("What is LIDAR?", "session-123")
    
    assert "LIDAR" in result["answer"]
    assert result["session_id"] == "session-123"
    
    # Verify Runner was called with correct config
    mock_runner_e2e.run.assert_called_once()
    call_kwargs = mock_runner_e2e.run.call_args[1]
    assert call_kwargs['max_turns'] == 10
    assert call_kwargs['run_config'].model == "gpt-4o-mini"

@pytest.mark.asyncio
async def test_rag_flow_out_of_scope(rag_agent, mock_runner_e2e):
    mock_result = MagicMock()
    mock_result.final_output = "This question appears to be outside the book's scope."
    mock_runner_e2e.run = AsyncMock(return_value=mock_result)
    
    result = await rag_agent.run("What is the capital of France?", "session-123")
    
    assert "outside the book's scope" in result["answer"]
