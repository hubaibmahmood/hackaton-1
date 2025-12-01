"""Qdrant vector database client and collection management."""
import logging

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse

from src.config import settings

logger = logging.getLogger(__name__)


class QdrantDB:
    """Qdrant vector database connection manager."""

    def __init__(self) -> None:
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = settings.qdrant_collection_name
        self.vector_size = settings.embedding_dimensions

    async def create_collection(self) -> bool:
        """Create Qdrant collection if it doesn't exist.

        Returns:
            bool: True if collection was created or already exists
        """
        try:
            # Check if collection already exists
            collections = self.client.get_collections().collections
            if any(col.name == self.collection_name for col in collections):
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True

            # Create new collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created collection '{self.collection_name}' successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False

    async def insert_test_vector(self) -> bool:
        """Insert a test vector to verify collection is working.

        Returns:
            bool: True if test vector was inserted successfully
        """
        try:
            # Create a test vector with correct dimensions
            test_vector = [0.0] * self.vector_size
            test_vector[0] = 1.0  # Set first element to 1.0 for non-zero vector

            # Insert test point
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=0,
                        vector=test_vector,
                        payload={
                            "text": "Test vector",
                            "chapter": "Test",
                            "section": "Test",
                        },
                    )
                ],
            )
            logger.info("Test vector inserted successfully")

            # Delete test vector
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[0],
            )
            logger.info("Test vector deleted successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to insert test vector: {e}")
            return False

    def search(
        self,
        query_vector: list[float],
        limit: int | None = None,
        score_threshold: float | None = None,
    ) -> list[dict]:
        """Search for similar vectors in the collection.

        Args:
            query_vector: Query embedding vector
            limit: Number of results to return (default from settings)
            score_threshold: Minimum similarity score (default from settings)

        Returns:
            List of search results with scores and metadata
        """
        if limit is None:
            limit = settings.top_k_results
        if score_threshold is None:
            score_threshold = settings.similarity_threshold

        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
            )
            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload,
                }
                for hit in results
            ]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def health_check(self) -> bool:
        """Check if Qdrant connection is healthy.

        Returns:
            bool: True if Qdrant is accessible, False otherwise
        """
        try:
            collections = self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False


# Global Qdrant instance
qdrant_db = QdrantDB()
