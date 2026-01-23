"""
RAG (Retrieval-Augmented Generation) Engine
"""
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
import time
from backend.services.embeddings import EmbeddingService
from backend.services.llm_client import LLMClient
from backend.core.security import get_security_guard
from backend.core.config import get_settings


class RAGEngine:
    """RAG engine for sentiment data queries"""
    
    def __init__(self):
        self.settings = get_settings()
        self.embedding_service = EmbeddingService()
        self.llm_client = LLMClient()
        self.security_guard = get_security_guard()
        
        # Initialize ChromaDB
        self.embedding_service.initialize_chromadb()
        
    def query(
        self,
        user_query: str,
        user_id: str = "anonymous",
        top_k: int = None,
        filters: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process a user query using RAG
        
        Args:
            user_query: User's question
            user_id: User identifier for rate limiting
            top_k: Number of chunks to retrieve
            filters: Metadata filters for retrieval
            conversation_history: Previous conversation
            
        Returns:
            Dict with response, sources, and metadata
        """
        start_time = time.time()
        
        # Security validation
        is_valid, reason, warning = self.security_guard.validate_query(user_query, user_id)
        if not is_valid:
            logger.warning(f"Query blocked: {reason}")
            return {
                'response': f"Query rejected: {reason}",
                'sources': [],
                'query_type': 'blocked',
                'processing_time': time.time() - start_time,
                'warning': None,
                'blocked': True
            }
        
        # Retrieve relevant chunks
        top_k = top_k or self.settings.retrieval_top_k
        retrieved_data = self._retrieve_chunks(user_query, top_k, filters)
        
        # Rerank results
        reranked_data = self._rerank_chunks(user_query, retrieved_data)
        
        # Build context
        context = self._build_context(reranked_data)
        
        # Generate response
        llm_response = self.llm_client.generate_response(
            query=user_query,
            context=context,
            conversation_history=conversation_history
        )
        
        # Sanitize response
        sanitized_response = self.security_guard.sanitize_response(llm_response['response'])
        
        # Validate response size
        is_valid_size, size_msg = self.security_guard.validate_response_size(sanitized_response)
        if not is_valid_size:
            logger.warning(f"Response too large: {size_msg}")
            sanitized_response = sanitized_response[:self.settings.max_response_tokens * 4] + "\n\n[Response truncated due to size limits]"
        
        # Prepare sources
        sources = self._format_sources(reranked_data)
        
        processing_time = time.time() - start_time
        
        return {
            'response': sanitized_response,
            'sources': sources,
            'query_type': self._classify_query(user_query),
            'processing_time': processing_time,
            'warning': warning,
            'blocked': False,
            'usage': llm_response.get('usage', {})
        }
    
    def _retrieve_chunks(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Retrieve relevant chunks from vector database"""
        try:
            results = self.embedding_service.query_similar_chunks(
                query=query,
                top_k=top_k,
                filter_dict=filters
            )
            
            logger.info(f"Retrieved {len(results['documents'])} chunks")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving chunks: {e}")
            return {
                'documents': [],
                'metadatas': [],
                'distances': [],
                'ids': []
            }
    
    def _rerank_chunks(self, query: str, retrieved_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rerank retrieved chunks based on relevance
        
        Simple reranking based on:
        1. Similarity score (distance)
        2. Chunk type priority (country_summary > monthly > weekly > daily)
        3. Recency (more recent data slightly preferred)
        """
        chunks = []
        
        for i in range(len(retrieved_data['documents'])):
            chunk = {
                'text': retrieved_data['documents'][i],
                'metadata': retrieved_data['metadatas'][i],
                'distance': retrieved_data['distances'][i],
                'id': retrieved_data['ids'][i]
            }
            
            # Calculate reranking score
            score = 1.0 - chunk['distance']  # Convert distance to similarity
            
            # Boost based on chunk type
            chunk_type = chunk['metadata'].get('type', 'unknown')
            type_boost = {
                'country_summary': 1.2,
                'monthly': 1.1,
                'weekly': 1.05,
                'daily': 1.0,
                'anomaly': 1.15
            }.get(chunk_type, 1.0)
            
            score *= type_boost
            
            chunk['rerank_score'] = score
            chunks.append(chunk)
        
        # Sort by reranking score
        chunks.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        return chunks
    
    def _build_context(self, chunks: List[Dict[str, Any]], max_chunks: int = 8) -> str:
        """Build context string from chunks"""
        context_parts = []
        
        for i, chunk in enumerate(chunks[:max_chunks]):
            chunk_type = chunk['metadata'].get('type', 'unknown')
            context_parts.append(f"[Source {i+1} - {chunk_type}]")
            context_parts.append(chunk['text'])
            context_parts.append("")  # Empty line between chunks
        
        return "\n".join(context_parts)
    
    def _format_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format sources for response"""
        sources = []
        
        for chunk in chunks[:5]:  # Top 5 sources
            source = {
                'chunk_id': chunk['id'],
                'chunk_type': chunk['metadata'].get('type', 'unknown'),
                'relevance_score': float(chunk['rerank_score']),
                'metadata': chunk['metadata']
            }
            sources.append(source)
        
        return sources
    
    def _classify_query(self, query: str) -> str:
        """Classify query type"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['predict', 'forecast', 'future', 'will be', 'next']):
            return 'forecast'
        elif any(word in query_lower for word in ['trend', 'trending', 'pattern', 'direction']):
            return 'trend'
        elif any(word in query_lower for word in ['correlate', 'correlation', 'relationship', 'related']):
            return 'correlation'
        elif any(word in query_lower for word in ['anomaly', 'unusual', 'outlier', 'spike', 'drop']):
            return 'anomaly'
        else:
            return 'historical'
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG engine statistics"""
        try:
            collection_stats = self.embedding_service.get_collection_stats()
            return {
                'status': 'operational',
                'collection_stats': collection_stats
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
