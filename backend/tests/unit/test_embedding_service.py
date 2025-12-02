"""Unit tests for embedding service."""
import pytest
from unittest.mock import MagicMock, patch
from src.services.embedding_service import EmbeddingService

@pytest.fixture
def mock_openai_client():
    with patch("src.services.embedding_service.OpenAI") as mock:
        yield mock

@pytest.fixture
def embedding_service(mock_openai_client):
    return EmbeddingService()

def test_generate_embedding_success(embedding_service, mock_openai_client):
    # Mock response
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
    mock_openai_client.return_value.embeddings.create.return_value = mock_response

    embedding = embedding_service.generate_embedding("test text")

    assert embedding == [0.1, 0.2, 0.3]
    mock_openai_client.return_value.embeddings.create.assert_called_once()

def test_generate_embedding_failure(embedding_service, mock_openai_client):
    # Mock failure
    mock_openai_client.return_value.embeddings.create.side_effect = Exception("API Error")

    with pytest.raises(Exception) as exc:
        embedding_service.generate_embedding("test text")
    
    assert "API Error" in str(exc.value)

def test_generate_embeddings_batch_success(embedding_service, mock_openai_client):
    # Mock response
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=[0.1, 0.1]),
        MagicMock(embedding=[0.2, 0.2])
    ]
    mock_openai_client.return_value.embeddings.create.return_value = mock_response

    embeddings = embedding_service.generate_embeddings_batch(["text1", "text2"])

    assert len(embeddings) == 2
    assert embeddings[0] == [0.1, 0.1]
    assert embeddings[1] == [0.2, 0.2]
