"""Content-related models for book chunks and citations."""
from typing import Optional

from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    """Source citation model for referencing book content."""

    chapter: str = Field(..., description="Chapter name or number")
    section: str = Field(..., description="Section within chapter")
    page_reference: Optional[str] = Field(None, description="Page or heading reference")
    excerpt_text: str = Field(..., description="Relevant text excerpt (max 200 chars)", max_length=200)
    citation_url: str = Field(..., description="URL to the specific section in the book")


class ChunkMetadata(BaseModel):
    """Metadata for book content chunks stored in vector database."""

    # Document identification
    document_id: str = Field(..., description="Unique document identifier")
    document_path: str = Field(..., description="File path (e.g., /docs/part-01/chapter-01/index.md)")
    document_url: str = Field(..., description="Public URL to the document")

    # Hierarchical structure
    part_number: Optional[int] = Field(None, description="Part number in book")
    part_name: Optional[str] = Field(None, description="Part name/title")
    chapter_number: Optional[int] = Field(None, description="Chapter number")
    chapter_title: str = Field(..., description="Chapter title")

    # Content structure
    heading_path: list[str] = Field(default_factory=list, description="Heading hierarchy")
    heading_level: int = Field(..., description="Heading level (2 or 3)")
    section_id: str = Field(..., description="Section anchor ID")

    # Chunk positioning
    chunk_index: int = Field(..., description="Index of chunk within document")
    chunk_id: str = Field(..., description="Unique chunk identifier")

    # Content characteristics
    content_type: str = Field(default="explanation", description="Type: explanation, example, exercise")
    contains_code: bool = Field(default=False, description="Whether chunk contains code blocks")
    code_languages: list[str] = Field(default_factory=list, description="Programming languages in code")
    contains_table: bool = Field(default=False, description="Whether chunk contains tables")

    # Contextual navigation
    prerequisite_chapters: list[str] = Field(default_factory=list, description="List of prerequisite chapters")
    next_topics: list[str] = Field(default_factory=list, description="List of upcoming topics/chapters")

    # Citation info
    citation_text: str = Field(..., description="Formatted citation text")
    citation_url: str = Field(..., description="Full URL with anchor")

    # Metrics
    token_count: int = Field(..., description="Number of tokens in chunk")
    character_count: int = Field(..., description="Number of characters")


class BookChunk(BaseModel):
    """Book content chunk with embedding."""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    text: str = Field(..., description="Chunk text content")
    embedding: Optional[list[float]] = Field(None, description="Embedding vector")
    metadata: ChunkMetadata = Field(..., description="Chunk metadata")
