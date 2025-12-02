"""Retrieval service for Qdrant vector search with enriched metadata."""

import hashlib
import json
import logging
from functools import lru_cache
from typing import Optional

from src.config import settings
from src.database.qdrant import qdrant_db
from src.models.content import SourceCitation

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for retrieving and enriching book content from Qdrant."""

    @lru_cache(maxsize=1000)
    def _get_cached_search(self, query_hash: str) -> list[dict]:
        """Simple LRU cache for search results (placeholder for Redis)."""
        return []  # Real implementation would return cached value if found

    def search_by_embedding(
        self,
        query_embedding: list[float],
        limit: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
    ) -> list[dict]:
        """Search Qdrant by embedding vector with similarity scoring.

        Args:
            query_embedding: Query embedding vector
            limit: Number of results to return (default from settings)
            similarity_threshold: Minimum similarity score (default from settings)

        Returns:
            List of search results with scores and metadata
        """
        if limit is None:
            limit = settings.top_k_results
        if similarity_threshold is None:
            # Optimization: Slightly higher default threshold for precision
            similarity_threshold = 0.7

        try:
            results = qdrant_db.search(
                query_vector=query_embedding,
                limit=limit,
                score_threshold=similarity_threshold,
            )

            logger.info(
                f"Retrieved {len(results)} chunks with threshold {similarity_threshold}"
            )
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def enrich_results_with_metadata(self, results: list[dict]) -> list[dict]:
        """Enrich search results with formatted metadata and citations.

        Args:
            results: Raw search results from Qdrant

        Returns:
            Enriched results with SourceCitation models
        """
        enriched_results = []

        for result in results:
            payload = result.get("payload", {})

            # Extract metadata
            chapter = payload.get("chapter", "Unknown Chapter")
            section = payload.get("section", "Unknown Section")
            page_reference = payload.get("page_reference")
            text = payload.get("text", "")
            citation_url = payload.get("citation_url", "")
            citation_text = payload.get("citation_text", "")

            # Create SourceCitation
            citation = SourceCitation(
                chapter=chapter,
                section=section,
                page_reference=page_reference,
                excerpt_text=text[:200],  # First 200 chars
                citation_url=citation_url,
            )

            enriched_results.append(
                {
                    "id": result.get("id"),
                    "score": result.get("score", 0.0),
                    "text": text,
                    "citation": citation.model_dump(),
                    "citation_text": citation_text,
                    "citation_url": citation_url,
                    "metadata": payload,
                }
            )

        logger.debug(f"Enriched {len(enriched_results)} results with metadata")
        return enriched_results

    def search_and_enrich(
        self,
        query_embedding: list[float],
        limit: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
    ) -> list[dict]:
        """Search and enrich results in one call.

        Args:
            query_embedding: Query embedding vector
            limit: Number of results to return
            similarity_threshold: Minimum similarity score

        Returns:
            Enriched search results with citations
        """
        results = self.search_by_embedding(
            query_embedding=query_embedding,
            limit=limit,
            similarity_threshold=similarity_threshold,
        )

        return self.enrich_results_with_metadata(results)


# Global retrieval service instance
retrieval_service = RetrievalService()
