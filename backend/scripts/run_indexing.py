import asyncio
import sys
import os
import logging

# Add backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from pathlib import Path
from src.indexing.indexer import ContentIndexer
from src.config import setup_logging

async def main():
    setup_logging()
    
    # Resolve docs dir relative to project root (assuming script is in backend/scripts/)
    # backend/scripts/run_indexing.py -> backend/scripts -> backend -> root
    project_root = Path(__file__).resolve().parent.parent.parent
    docs_dir = project_root / "book" / "docs"
    
    print(f"Starting indexing process from {docs_dir}...")
    
    # Initialize indexer with correct path
    indexer = ContentIndexer(docs_dir=str(docs_dir))
    
    try:
        result = await indexer.index_all()
        print(f"Indexing completed: {result}")
    except Exception as e:
        print(f"Indexing failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
