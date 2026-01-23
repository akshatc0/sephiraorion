"""
Tests for RAG engine
"""
import pytest
from unittest.mock import Mock, patch
from backend.core.rag_engine import RAGEngine


class TestRAGEngine:
    """Test RAG engine functionality"""
    
    @pytest.fixture
    def mock_embedding_service(self):
        """Mock embedding service"""
        with patch('backend.core.rag_engine.EmbeddingService') as mock:
            service = Mock()
            service.query_similar_chunks.return_value = {
                'documents': ['Sample document 1', 'Sample document 2'],
                'metadatas': [
                    {'type': 'daily', 'date': '2020-01-01'},
                    {'type': 'monthly', 'date': '2020-01'}
                ],
                'distances': [0.1, 0.2],
                'ids': ['chunk_1', 'chunk_2']
            }
            service.get_collection_stats.return_value = {
                'total_chunks': 100,
                'chunk_types_sample': {'daily': 50, 'monthly': 30}
            }
            mock.return_value = service
            yield service
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client"""
        with patch('backend.core.rag_engine.LLMClient') as mock:
            client = Mock()
            client.generate_response.return_value = {
                'response': 'The sentiment in the United States was 6.8 in 2020.',
                'finish_reason': 'stop',
                'usage': {
                    'prompt_tokens': 100,
                    'completion_tokens': 50,
                    'total_tokens': 150
                }
            }
            mock.return_value = client
            yield client
    
    def test_query_classification(self):
        """Test query type classification"""
        engine = RAGEngine()
        
        assert engine._classify_query("What will the sentiment be next month?") == 'forecast'
        assert engine._classify_query("Show me the trend for United States") == 'trend'
        assert engine._classify_query("Are US and UK sentiments correlated?") == 'correlation'
        assert engine._classify_query("What was the sentiment in 2020?") == 'historical'
    
    def test_reranking(self):
        """Test chunk reranking"""
        engine = RAGEngine()
        
        retrieved_data = {
            'documents': ['Doc 1', 'Doc 2', 'Doc 3'],
            'metadatas': [
                {'type': 'daily'},
                {'type': 'country_summary'},
                {'type': 'monthly'}
            ],
            'distances': [0.3, 0.2, 0.1],
            'ids': ['1', '2', '3']
        }
        
        reranked = engine._rerank_chunks("test query", retrieved_data)
        
        # Check that reranking was applied
        assert len(reranked) == 3
        assert all('rerank_score' in chunk for chunk in reranked)
        
        # Country summary should be boosted
        country_summary_chunk = next(c for c in reranked if c['metadata']['type'] == 'country_summary')
        assert country_summary_chunk['rerank_score'] > 0
    
    def test_context_building(self):
        """Test context string building"""
        engine = RAGEngine()
        
        chunks = [
            {
                'text': 'Text 1',
                'metadata': {'type': 'daily'},
                'rerank_score': 0.9,
                'id': '1'
            },
            {
                'text': 'Text 2',
                'metadata': {'type': 'monthly'},
                'rerank_score': 0.8,
                'id': '2'
            }
        ]
        
        context = engine._build_context(chunks)
        
        assert 'Text 1' in context
        assert 'Text 2' in context
        assert '[Source 1 - daily]' in context
        assert '[Source 2 - monthly]' in context
    
    def test_format_sources(self):
        """Test source formatting"""
        engine = RAGEngine()
        
        chunks = [
            {
                'id': 'chunk_1',
                'metadata': {'type': 'daily', 'date': '2020-01-01'},
                'rerank_score': 0.9
            }
        ]
        
        sources = engine._format_sources(chunks)
        
        assert len(sources) == 1
        assert sources[0]['chunk_id'] == 'chunk_1'
        assert sources[0]['chunk_type'] == 'daily'
        assert 'relevance_score' in sources[0]


class TestChunking:
    """Test chunking strategies"""
    
    def test_daily_chunks(self):
        """Test daily chunk creation"""
        import pandas as pd
        from backend.utils.chunking import SentimentChunker
        
        # Create sample data
        df = pd.DataFrame({
            'date': ['2020-01-01', '2020-01-02'],
            'United States': [6.5, 6.6],
            'United Kingdom': [7.0, 7.1]
        })
        
        chunker = SentimentChunker(df)
        chunks = chunker.create_daily_chunks()
        
        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('metadata' in chunk for chunk in chunks)
        assert all(chunk['chunk_type'] == 'daily' for chunk in chunks)
    
    def test_country_summary_chunks(self):
        """Test country summary chunk creation"""
        import pandas as pd
        from backend.utils.chunking import SentimentChunker
        
        # Create sample data
        df = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=100),
            'United States': [6.5 + i*0.01 for i in range(100)]
        })
        
        chunker = SentimentChunker(df)
        chunks = chunker.create_country_summary_chunks()
        
        assert len(chunks) > 0
        assert all('United States' in chunk['text'] or 'Country:' in chunk['text'] for chunk in chunks)
        assert all(chunk['chunk_type'] == 'country_summary' for chunk in chunks)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
