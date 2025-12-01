"""Configuration management using Pydantic Settings."""
import logging
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")

    # Qdrant Configuration
    qdrant_url: str = Field(..., description="Qdrant instance URL")
    qdrant_api_key: str | None = Field(None, description="Qdrant API key (optional for local)")
    qdrant_collection_name: str = Field(default="book_content", description="Qdrant collection name")

    # Neon Postgres Configuration
    neon_db_url: str = Field(..., description="Neon Postgres connection string")

    # CORS Configuration
    frontend_origin: str = Field(
        default="http://localhost:3000",
        description="Frontend origin for CORS"
    )

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )

    # Session Configuration
    session_expiry_hours: int = Field(default=24, description="Session expiry in hours")
    rate_limit_queries_per_minute: int = Field(default=10, description="Rate limit per session")

    # AI Model Configuration
    chat_model: str = Field(default="gpt-4o-mini", description="OpenAI chat model for agents")
    embedding_model: str = Field(default="text-embedding-3-small", description="OpenAI embedding model")
    embedding_dimensions: int = Field(default=1536, description="Embedding vector dimensions")

    # RAG Configuration
    similarity_threshold: float = Field(default=0.5, description="Minimum similarity score for retrieval")
    top_k_results: int = Field(default=5, description="Number of chunks to retrieve")
    chunk_size_tokens: int = Field(default=450, description="Target chunk size in tokens")
    chunk_overlap_tokens: int = Field(default=60, description="Overlap between chunks in tokens")


# Global settings instance
settings = Settings()


def setup_logging() -> None:
    """Configure structured logging."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
