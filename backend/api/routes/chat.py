"""
Chat endpoints for RAG queries
"""
from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from loguru import logger

from backend.models.schemas import ChatRequest, ChatResponse
from backend.core.rag_engine import RAGEngine

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Initialize RAG engine (will be initialized once)
rag_engine = None


def get_rag_engine():
    """Get or initialize RAG engine"""
    global rag_engine
    if rag_engine is None:
        rag_engine = RAGEngine()
    return rag_engine


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    """
    Chat with Sephira using RAG
    
    Process user queries about sentiment data with context-aware responses.
    """
    try:
        # Get user ID from request (could be from auth token, session, etc.)
        user_id = http_request.client.host  # Use IP as simple user ID
        
        # Get RAG engine
        engine = get_rag_engine()
        
        # Build filters if provided
        filters = None
        if request.countries or request.start_date or request.end_date:
            filters = {}
            # Note: ChromaDB filtering would need proper metadata structure
            # For now, we'll handle filtering in post-processing
        
        # Query RAG engine
        result = engine.query(
            user_query=request.query,
            user_id=user_id,
            filters=filters,
            conversation_history=None  # Could store session history
        )
        
        # Check if blocked
        if result.get('blocked', False):
            raise HTTPException(status_code=403, detail=result['response'])
        
        return ChatResponse(
            response=result['response'],
            sources=result['sources'],
            query_type=result['query_type'],
            processing_time=result['processing_time'],
            warning=result.get('warning')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    """Get RAG engine statistics"""
    try:
        engine = get_rag_engine()
        stats = engine.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
