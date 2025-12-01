"""Indexing API endpoints."""
import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException

from src.indexing.indexer import indexer

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/")
async def trigger_indexing(background_tasks: BackgroundTasks):
    """Trigger content indexing in the background.
    
    Returns:
        Status message
    """
    try:
        # Run indexing in background to not block response
        background_tasks.add_task(indexer.index_all)
        return {"status": "accepted", "message": "Indexing started in background"}
    except Exception as e:
        logger.error(f"Failed to trigger indexing: {e}")
        raise HTTPException(status_code=500, detail=str(e))
