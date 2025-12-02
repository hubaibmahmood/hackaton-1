"""Content indexing pipeline orchestrator."""
import logging
import os
from typing import List
from pathlib import Path
import uuid

from src.indexing.chunker import chunker
from src.services.embedding_service import embedding_service
from src.database.qdrant import qdrant_db
from src.models.content import BookChunk

logger = logging.getLogger(__name__)

class ContentIndexer:
    """Orchestrates the indexing of book content."""

    def __init__(self, docs_dir: str = "book/docs"):
        """Initialize indexer with documents directory."""
        self.docs_dir = Path(docs_dir)
        # Batch size for embedding and upserting
        self.batch_size = 20

    async def index_all(self) -> dict:
        """Index all content in the documents directory.
        
        Returns:
            Stats about the indexing process
        """
        logger.info(f"Starting indexing from {self.docs_dir}")
        
        if not self.docs_dir.exists():
            logger.error(f"Documents directory not found: {self.docs_dir}")
            return {"status": "error", "message": "Docs dir not found"}

        # Ensure collection exists
        await qdrant_db.create_collection()

        files = list(self.docs_dir.rglob("*.md")) + list(self.docs_dir.rglob("*.mdx"))
        total_files = len(files)
        total_chunks = 0
        
        logger.info(f"Found {total_files} files to index")
        
        all_chunks: List[BookChunk] = []
        
        # 1. Parse and Chunk
        for i, file_path in enumerate(files):
            try:
                logger.info(f"Processing [{i+1}/{total_files}]: {file_path}")
                file_chunks = chunker.parse_file(str(file_path))
                all_chunks.extend(file_chunks)
            except Exception as e:
                logger.error(f"Failed to parse {file_path}: {e}")

        logger.info(f"Total extracted chunks: {len(all_chunks)}")
        
        # 2. Embed and Upsert in batches
        total_chunks = len(all_chunks)
        processed_chunks = 0
        
        for i in range(0, total_chunks, self.batch_size):
            batch = all_chunks[i : i + self.batch_size]
            
            try:
                # Prepare texts for embedding
                texts = [chunk.text for chunk in batch]
                
                # Generate embeddings
                embeddings = embedding_service.generate_embeddings_batch(texts)
                
                # Prepare Qdrant points
                points = []
                for chunk, embedding in zip(batch, embeddings):
                    # Generate a consistent UUID from the chunk_id string
                    # Qdrant requires UUID or int IDs
                    chunk_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, chunk.chunk_id))
                    
                    points.append({
                        "id": chunk_uuid,
                        "vector": embedding,
                        "payload": {
                            "text": chunk.text,
                            "chunk_id": chunk.chunk_id,
                            **chunk.metadata.model_dump(mode='json')
                        }
                    })
                
                # Upsert batch
                success = await qdrant_db.upsert_chunks(points)
                if success:
                    processed_chunks += len(batch)
                    logger.info(f"Indexed batch {i}-{i+len(batch)} ({processed_chunks}/{total_chunks})")
                else:
                    logger.error(f"Failed to upsert batch {i}")

            except Exception as e:
                logger.error(f"Error processing batch {i}: {e}")

        return {
            "status": "completed",
            "files_processed": total_files,
            "chunks_indexed": processed_chunks,
            "total_chunks_extracted": total_chunks
        }

# Global indexer instance
indexer = ContentIndexer()
