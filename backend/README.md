# RAG Chatbot Backend

FastAPI backend for the Physical AI textbook chatbot using OpenAI Agents SDK and RAG.

## Features

- ✅ **OpenAI Agents SDK** - Custom tools with automatic execution
- ✅ **RAG Pipeline** - Qdrant vector database + OpenAI embeddings
- ✅ **Session Management** - Postgres with conversation history
- ✅ **Rate Limiting** - 10 queries/minute per session
- ✅ **Streaming Responses** - Server-Sent Events (SSE)
- ✅ **CORS Enabled** - Ready for frontend integration

## Tech Stack

- **Framework**: FastAPI 0.104+
- **AI/ML**: OpenAI Agents SDK, OpenAI GPT-4o-mini, text-embedding-3-small
- **Databases**: Qdrant (vectors), Neon Postgres (sessions)
- **Python**: 3.12
- **Package Manager**: uv (Rust-based)

## Setup

### 1. Prerequisites

- Python 3.12+
- uv package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Qdrant Cloud account (free tier)
- Neon Serverless Postgres (free tier)
- OpenAI API key

### 2. Install Dependencies

```bash
cd backend
uv sync
```

### 3. Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

Required variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `QDRANT_URL` - Qdrant instance URL
- `QDRANT_API_KEY` - Qdrant API key (optional for local)
- `NEON_DB_URL` - Neon Postgres connection string
- `FRONTEND_ORIGIN` - Frontend URL for CORS (default: http://localhost:3000)
- `CHAT_MODEL` - OpenAI chat model (default: gpt-4o-mini)

### 4. Run Migrations

```bash
uv run python -m src.database.migrate
```

### 5. Create Qdrant Collection

```bash
uv run python -c "
import asyncio
from src.database.qdrant import qdrant_db

async def setup():
    await qdrant_db.create_collection()
    await qdrant_db.insert_test_vector()

asyncio.run(setup())
"
```

### 6. Start Server

```bash
# Development
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Chat (Regular)
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "What is a ROS2 node?",
  "session_id": "optional-uuid",
  "selected_text": "optional-selected-text",
  "current_page_url": "optional-page-url"
}
```

### Chat (Streaming)
```bash
POST /api/chat/stream
Content-Type: application/json
Accept: text/event-stream

{
  "message": "What is a ROS2 node?"
}
```

## Project Structure

```
backend/
├── src/
│   ├── config.py              # Pydantic Settings
│   ├── main.py                # FastAPI app
│   ├── database/
│   │   ├── postgres.py        # Postgres connection
│   │   ├── qdrant.py          # Qdrant client
│   │   └── migrations/        # SQL migrations
│   ├── models/
│   │   ├── query.py           # Request/response models
│   │   ├── content.py         # Citation models
│   │   └── session.py         # Session models
│   ├── services/
│   │   ├── embedding_service.py    # OpenAI embeddings
│   │   ├── session_service.py      # Session management
│   │   └── retrieval_service.py    # Qdrant search
│   ├── agents/
│   │   ├── tools.py           # Custom @function_tool
│   │   └── rag_agent.py       # OpenAI Agents SDK
│   └── api/
│       ├── middleware.py      # Error handling
│       └── chat.py            # Chat endpoints
└── tests/
    ├── unit/
    ├── integration/
    └── ...
```

## Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_embedding_service.py

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

## Docker

```bash
# Build
docker build -t rag-chatbot-backend .

# Run
docker run -p 8000:8000 --env-file .env rag-chatbot-backend
```

## Deployment (Render)

1. Connect GitHub repository
2. Select `backend/` as root directory
3. Set environment variables in Render dashboard
4. Deploy automatically on push

See `render.yaml` for configuration.

## OpenAI Agents SDK Usage

The backend uses the OpenAI Agents SDK for intelligent tool calling:

```python
from agents import Agent, function_tool, Runner

# Define custom tool
@function_tool
async def search_book_content(query: str) -> str:
    # Your implementation
    pass

# Create agent
agent = Agent(
    name="Physical AI Assistant",
    instructions="You are a helpful assistant...",
    model="gpt-4o-mini",  # Cost-optimized model
    tools=[search_book_content],
)

# Run agent
result = await Runner.run(agent, "What is a ROS2 node?")
```

## Troubleshooting

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database connection errors
- Verify Neon connection string is correct
- Check if Neon Postgres is active (free tier auto-pauses)

### Qdrant errors
- Verify Qdrant URL and API key
- Ensure collection exists: run create_collection script

## License

MIT
