"""
Configuration management for Sephira Orion
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-5.1"
    openai_embedding_model: str = "text-embedding-3-large"
    
    # External API Keys
    news_api_key: Optional[str] = None
    alpha_vantage_key: Optional[str] = None
    fred_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    
    # Database Configuration
    chromadb_path: str = "./data/chroma"
    
    # Security Settings
    max_queries_per_minute: int = 10
    max_queries_per_hour: int = 100
    max_response_tokens: int = 2000
    
    # Application Settings
    log_level: str = "INFO"
    environment: str = "development"
    
    # Data paths
    data_path: str = "./data/raw/all_indexes_beta.csv"
    processed_data_path: str = "./data/processed"
    
    # RAG Settings
    retrieval_top_k: int = 10
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Redis (optional)
    redis_url: Optional[str] = None
    enable_cache: bool = False
    
    # Rate limiting
    rate_limit_enabled: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
