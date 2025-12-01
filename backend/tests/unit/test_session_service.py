"""Unit tests for session service."""
import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch, AsyncMock

from src.services.session_service import SessionService, RateLimitExceeded
from src.models.session import UserSession

@pytest.fixture
def mock_postgres_db():
    with patch("src.services.session_service.postgres_db") as mock:
        # Mock get_connection context manager
        mock_conn = AsyncMock()
        mock.get_connection.return_value.__aenter__.return_value = mock_conn
        yield mock

@pytest.fixture
def session_service(mock_postgres_db):
    return SessionService()

@pytest.mark.asyncio
async def test_create_session(session_service, mock_postgres_db):
    session = await session_service.create_session()
    
    assert isinstance(session, UserSession)
    assert session.session_id is not None
    # Verify DB insert called
    mock_postgres_db.get_connection.return_value.__aenter__.return_value.execute.assert_called_once()

@pytest.mark.asyncio
async def test_validate_session_valid(session_service, mock_postgres_db):
    # Mock load_session
    session_id = uuid4()
    mock_session = UserSession(session_id=session_id)
    
    with patch.object(session_service, 'load_session', return_value=mock_session) as mock_load:
        is_valid = await session_service.validate_session(session_id)
        assert is_valid is True

@pytest.mark.asyncio
async def test_validate_session_expired(session_service, mock_postgres_db):
    session_id = uuid4()
    # Create expired session
    expired_time = datetime.now(timezone.utc) - timedelta(hours=25)
    mock_session = UserSession(session_id=session_id, expires_at=expired_time)
    
    with patch.object(session_service, 'load_session', return_value=mock_session) as mock_load:
        is_valid = await session_service.validate_session(session_id)
        assert is_valid is False

@pytest.mark.asyncio
async def test_check_rate_limit_exceeded(session_service, mock_postgres_db):
    session_id = uuid4()
    # Mock session at limit
    mock_session = UserSession(
        session_id=session_id,
        rate_limit_counter=100, # Assuming limit is < 100
        rate_limit_window_start=datetime.now(timezone.utc)
    )
    
    with patch.object(session_service, 'load_session', return_value=mock_session):
        with pytest.raises(RateLimitExceeded):
            await session_service.check_rate_limit(session_id)
