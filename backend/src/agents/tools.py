"""Custom tools for OpenAI Agents SDK - Qdrant retrieval."""
import logging
from typing import Annotated

from agents import function_tool

from src.database.qdrant import qdrant_db
from src.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


@function_tool
async def search_book_content(
    query: Annotated[str, "The search query to find relevant book content"]
) -> str:
    """Search the Physical AI textbook for relevant content using vector similarity.

    This tool searches through the book's content using semantic search to find
    passages relevant to the user's question. It returns the most relevant text
    chunks along with their source citations.

    Args:
        query: The search query text to find relevant book sections

    Returns:
        Formatted string containing relevant text chunks with citations
    """
    try:
        logger.info(f"Searching book content for query: {query[:50]}...")

        # Generate embedding for the query
        query_embedding = embedding_service.generate_embedding(query)

        # Search Qdrant for similar chunks
        results = qdrant_db.search(
            query_vector=query_embedding,
            limit=5,  # Top 5 results
            score_threshold=0.7,  # Minimum similarity
        )

        if not results:
            return "No relevant content found in the book for this query. This topic may be outside the book's scope."

        # Format results for agent
        formatted_output = []
        for idx, result in enumerate(results, 1):
            payload = result.get("payload", {})
            text = payload.get("text", "")
            chapter = payload.get("chapter", "Unknown")
            section = payload.get("section", "Unknown")
            citation_url = payload.get("citation_url", "")
            citation_text = payload.get("citation_text", "")
            similarity_score = result.get("score", 0.0)

            formatted_output.append(
                f"Result {idx} (Relevance: {similarity_score:.2f}):\n"
                f"Source: {citation_text}\n"
                f"Content: {text}\n"
                f"URL: {citation_url}\n"
            )

        logger.info(f"Found {len(results)} relevant chunks")
        return "\n---\n".join(formatted_output)

    except Exception as e:
        logger.error(f"Error searching book content: {e}")
        return f"Error searching book content: {str(e)}"
