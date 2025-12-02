# Quickstart Guide: RAG Chatbot

## Overview

This guide helps developers set up the RAG Chatbot environment locally.

## Developer Setup

### Prerequisites

- **Python 3.12+**
- **Node.js 18+**
- **Docker** (for local Qdrant/Postgres)
- **uv** (Python package manager)

### Backend Setup

1.  **Navigate to backend**:
    ```bash
    cd backend
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

3.  **Configure Environment**:
    Copy `.env.example` to `.env` and fill in your keys:
    ```bash
    cp .env.example .env
    ```
    Required keys: `OPENAI_API_KEY`, `QDRANT_URL` (or use local), `NEON_DB_URL` (or local Postgres).

4.  **Run Infrastructure (Optional)**:
    If running databases locally:
    ```bash
    docker-compose up -d
    ```

5.  **Run Migrations**:
    ```bash
    uv run python src/database/migrate.py
    ```

6.  **Start Server**:
    ```bash
    uv run uvicorn src.main:app --reload
    ```
    Backend will be available at `http://localhost:8000`.

### Frontend Setup

1.  **Navigate to book**:
    ```bash
    cd book
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    ```

3.  **Start Docusaurus**:
    ```bash
    npm start
    ```
    Book will be available at `http://localhost:3000`.

### Running Tests

- **Backend**: `uv run pytest`
- **Frontend**: `npm test`
