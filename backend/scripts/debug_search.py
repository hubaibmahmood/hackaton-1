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
    print("Debugging 'What is Physical AI?' query...")
    
    queries = ["Physical AI", "What is Physical AI?"]
    
    for query in queries:
        print(f"\nSearching for: '{query}'")
        
        # Generate embedding
        embedding = embedding_service.generate_embedding(query)
        
        # Search Qdrant with a very low threshold to see what's actually there
        results = qdrant_db.search(query_vector=embedding, limit=5, score_threshold=0.0)
        
        print(f"Found {len(results)} results (showing top 5):")
        for i, result in enumerate(results):
            payload = result["payload"]
            print(f"--- Result {i+1} (Score: {result['score']:.4f}) ---")
            print(f"Text: {payload.get('text', '')[:100]}...")
            print(f"Metadata: Chapter='{payload.get('chapter_title')}', Section='{payload.get('section_id')}'")

if __name__ == "__main__":
    asyncio.run(main())

