"""
Web search service using Tavily API
"""
from typing import Dict, Any, List, Optional
from loguru import logger
from backend.core.config import get_settings

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    logger.warning("Tavily package not installed. Web search will not be available.")


class WebSearchService:
    """Service for web searching using Tavily"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        
        if TAVILY_AVAILABLE and self.settings.tavily_api_key:
            try:
                self.client = TavilyClient(api_key=self.settings.tavily_api_key)
                logger.info("Tavily web search client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Tavily client: {e}")
        else:
            logger.warning("Tavily API key not configured or package not available")
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "advanced",
        include_answer: bool = True,
        include_raw_content: bool = False
    ) -> Dict[str, Any]:
        """
        Search the web using Tavily
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            search_depth: "basic" or "advanced" (advanced is more thorough)
            include_answer: Whether to include AI-generated answer
            include_raw_content: Whether to include raw page content
            
        Returns:
            Dict with search results and answer
        """
        if not self.client:
            return {
                'error': 'Web search not available. Tavily API key not configured.',
                'results': [],
                'answer': None
            }
        
        try:
            logger.info(f"Searching web for: {query}")
            
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_answer=include_answer,
                include_raw_content=include_raw_content
            )
            
            # Format results
            results = []
            for result in response.get('results', []):
                results.append({
                    'title': result.get('title'),
                    'url': result.get('url'),
                    'content': result.get('content'),
                    'score': result.get('score', 0),
                    'published_date': result.get('published_date')
                })
            
            return {
                'query': query,
                'answer': response.get('answer'),
                'results': results,
                'search_depth': search_depth,
                'total_results': len(results)
            }
            
        except Exception as e:
            logger.error(f"Error performing web search: {e}")
            return {
                'error': str(e),
                'results': [],
                'answer': None
            }
    
    def quick_answer(self, query: str) -> Optional[str]:
        """
        Get a quick answer to a query without full search results
        
        Args:
            query: Search query
            
        Returns:
            Answer string or None
        """
        result = self.search(query, max_results=3, search_depth="basic")
        return result.get('answer')
    
    def is_available(self) -> bool:
        """Check if web search is available"""
        return self.client is not None


# Singleton instance
_web_search_service = None


def get_web_search_service() -> WebSearchService:
    """Get singleton web search service instance"""
    global _web_search_service
    if _web_search_service is None:
        _web_search_service = WebSearchService()
    return _web_search_service
