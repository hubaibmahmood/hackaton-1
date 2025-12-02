"""Custom tools for OpenAI Agents SDK - Qdrant retrieval."""
import logging
from typing import Annotated

from agents import function_tool

from src.services.embedding_service import embedding_service
from src.services.retrieval_service import retrieval_service

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

        # Detect search/discovery intent to increase limit
        limit = None
        lower_query = query.lower()
        if any(phrase in lower_query for phrase in ["where is", "find", "show me all", "list all", "search for"]):
            logger.info("Search intent detected - increasing retrieval limit")
            limit = 10

        # Generate embedding for the query
        query_embedding = embedding_service.generate_embedding(query)

        # Search Qdrant using retrieval service (handles thresholding and limits from settings)
        results = retrieval_service.search_and_enrich(
            query_embedding=query_embedding,
            limit=limit
        )

        if not results:
            return "No relevant content found in the book for this query. This topic may be outside the book's scope."

        # Format results for agent
        formatted_output = []
        for idx, result in enumerate(results, 1):
            text = result.get("text", "")
            citation_metadata = result.get("citation", {}) # This is the full citation dict
            
            citation_text_for_display = citation_metadata.get("chapter", "Unknown")
            if citation_metadata.get("section"):
                citation_text_for_display += f", {citation_metadata.get("section")}"
            
            # The agent instruction is "According to [Citation Source]: [fact] ([URL])"
            formatted_output.append(
                f"According to {citation_text_for_display}: {text} ({citation_metadata.get("citation_url", "")})"
            )

        logger.info(f"Found {len(results)} relevant chunks")
        return "\n---\n".join(formatted_output)

    except Exception as e:
        logger.error(f"Error searching book content: {e}")
        return f"Error searching book content: {str(e)}"
