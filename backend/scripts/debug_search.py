import argparse
import asyncio
import logging
import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from src.config import setup_logging
from src.database.qdrant import qdrant_db
from src.services.embedding_service import embedding_service


async def main():
    parser = argparse.ArgumentParser(description="Debug Qdrant search retrieval.")
    parser.add_argument("--question", type=str, required=True, help="The question to search for.")
    parser.add_argument("--score_threshold", type=float, default=0.6, help="Minimum score threshold for Qdrant search results.")
    
    args = parser.parse_args()

    setup_logging()
    
    print(f"Debugging query: '{args.question}' with threshold: {args.score_threshold}")
    
    # Generate embedding
    embedding = embedding_service.generate_embedding(args.question)
    
    # Search Qdrant
    results = qdrant_db.search(
        query_vector=embedding, 
        limit=5, 
        score_threshold=args.score_threshold
    )

    print(f"Found {len(results)} results (showing top 5):")
    for i, result in enumerate(results):
        payload = result["payload"]
        print(f"--- Result {i + 1} (Score: {result['score']:.4f}) ---")
        print(f"Text: {payload.get('text', '')[:100]}...")
        print(
            f"Metadata: Chapter='{payload.get('chapter_title')}', Section='{payload.get('section_id')}'"
        )


if __name__ == "__main__":
    asyncio.run(main())
