# RAG Chatbot Backend

This is the backend service for the Physical AI Textbook Chatbot, built with FastAPI, OpenAI Agents SDK, and Qdrant.

## Deployment Guide (Render)

This service is configured for deployment on [Render](https://render.com).

### Prerequisites

1.  **Render Account**: Create an account at [render.com](https://render.com).
2.  **GitHub Repository**: Ensure this repository is connected to your Render account.
3.  **External Services**:
    *   **OpenAI API Key**: You need a valid API key.
    *   **Qdrant Cloud**: Create a cluster at [cloud.qdrant.io](https://cloud.qdrant.io) and get the URL and API Key.
    *   **Neon Postgres**: Create a database at [neon.tech](https://neon.tech) and get the connection string.

### Setup Instructions

1.  **New Web Service**: In Render dashboard, click "New +" -> "Web Service".
2.  **Connect Repo**: Select your repository.
3.  **Configuration**:
    *   **Name**: `rag-chatbot-backend` (or similar)
    *   **Region**: Choose one close to your users.
    *   **Branch**: `main` (or your deployment branch)
    *   **Root Directory**: `.` (project root)
    *   **Runtime**: `Docker`
    *   **Instance Type**: `Free` (for testing) or `Starter` ($7/mo) for production to avoid cold starts.

4.  **Environment Variables**:
    Add the following environment variables in the "Environment" tab:

    | Key | Value Description |
    | :--- | :--- |
    | `PYTHON_VERSION` | `3.12` |
    | `OPENAI_API_KEY` | Your OpenAI API Key (sk-...) |
    | `QDRANT_URL` | Your Qdrant Cluster URL (https://...) |
    | `QDRANT_API_KEY` | Your Qdrant API Key |
    | `NEON_DB_URL` | Postgres connection string (postgres://...) |
    | `FRONTEND_ORIGIN` | URL of your deployed book (e.g., https://hubaibmahmood.github.io) |
    | `LOG_LEVEL` | `INFO` |
    | `ENVIRONMENT` | `production` |

5.  **Deploy**: Click "Create Web Service". Render will build the Docker image and deploy it.

### Cron Job (Daily Indexing)

To ensure the chatbot's knowledge is up-to-date:

1.  **New Cron Job**: In Render dashboard, click "New +" -> "Cron Job".
2.  **Connect Repo**: Select the same repository.
3.  **Configuration**:
    *   **Name**: `daily-indexing`
    *   **Schedule**: `0 2 * * *` (Daily at 2 AM UTC)
    *   **Command**: `uv run python -m src.indexing.scheduler`
    *   **Root Directory**: `.`
    *   **Runtime**: `Docker`
4.  **Environment Variables**: Add the same variables as the Web Service.

### Verification

Once deployed, visit your service URL + `/health` (e.g., `https://rag-chatbot-backend.onrender.com/health`) to verify it returns `{"status": "ok"}`.