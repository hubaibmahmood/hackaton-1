import asyncio
import sys
import os
import logging

# Add backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from src.database.qdrant import qdrant_db
from src.services.embedding_service import embedding_service
from src.config import setup_logging

async def main():
    setup_logging()
    print("Validating indexing...")
    
    query = "lidar"
    print(f"Searching for: {query}")
    
    # Check collection count
    try:
        count_result = qdrant_db.client.count(collection_name=qdrant_db.collection_name)
        print(f"Total points in collection: {count_result.count}")
    except Exception as e:
        print(f"Failed to get count: {e}")

    # Generate embedding
    embedding = embedding_service.generate_embedding(query)
    
    # Search Qdrant with lower threshold
    results = qdrant_db.search(query_vector=embedding, limit=3, score_threshold=0.1)
    
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results):
        payload = result["payload"]
        print(f"--- Result {i+1} (Score: {result['score']:.4f}) ---")
        print(f"Text: {payload.get('text', '')[:100]}...")
        print(f"Metadata: Chapter='{payload.get('chapter_title')}', Section='{payload.get('section_id')}'")
        print(f"Source: {payload.get('document_path')}")

if __name__ == "__main__":
    asyncio.run(main())
