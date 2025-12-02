-- Migration 001: Create sessions table
-- Purpose: Store user sessions for conversation history and rate limiting

CREATE TABLE IF NOT EXISTS sessions (
    -- Primary key
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Conversation history
    conversation_history JSONB NOT NULL DEFAULT '[]'::jsonb,

    -- Rate limiting
    rate_limit_counter INTEGER NOT NULL DEFAULT 0,
    rate_limit_window_start TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Session management
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW() + INTERVAL '24 hours',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Optional metadata (no PII)
    current_page_url TEXT,
    user_agent TEXT
);

-- Index for cleanup of expired sessions
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);

-- Index for last activity tracking
CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON sessions(last_activity);

-- Comments for documentation
COMMENT ON TABLE sessions IS 'User sessions for chatbot conversations (no authentication, no PII)';
COMMENT ON COLUMN sessions.session_id IS 'Unique session identifier (UUID v4)';
COMMENT ON COLUMN sessions.conversation_history IS 'Array of conversation messages in JSONB format';
COMMENT ON COLUMN sessions.rate_limit_counter IS 'Number of queries in current time window';
COMMENT ON COLUMN sessions.rate_limit_window_start IS 'Start of current rate limit window';
COMMENT ON COLUMN sessions.expires_at IS 'Session expiration timestamp (default 24 hours)';
