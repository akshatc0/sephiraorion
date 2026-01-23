"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum


class QueryType(str, Enum):
    """Types of queries"""
    HISTORICAL = "historical"
    FORECAST = "forecast"
    TREND = "trend"
    CORRELATION = "correlation"
    ANOMALY = "anomaly"


class ChatRequest(BaseModel):
    """Chat request schema"""
    query: str = Field(..., min_length=1, max_length=1000)
    countries: Optional[List[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response schema"""
    response: str
    sources: List[Dict[str, Any]]
    query_type: str
    processing_time: float
    warning: Optional[str] = None


class ForecastRequest(BaseModel):
    """Forecast request schema"""
    country: str
    days: int = Field(default=30, ge=1, le=90)
    confidence_level: float = Field(default=0.95, ge=0.8, le=0.99)


class ForecastResponse(BaseModel):
    """Forecast response schema"""
    country: str
    forecasts: List[Dict[str, Any]]
    model_info: Dict[str, Any]
    accuracy_metrics: Optional[Dict[str, float]] = None


class TrendRequest(BaseModel):
    """Trend analysis request"""
    countries: List[str]
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    window: int = Field(default=30, ge=7, le=365)


class TrendResponse(BaseModel):
    """Trend analysis response"""
    trends: Dict[str, Any]
    analysis: str
    charts: Optional[List[Dict[str, Any]]] = None


class CorrelationRequest(BaseModel):
    """Correlation analysis request"""
    countries: Optional[List[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    method: str = Field(default="pearson", pattern="^(pearson|spearman)$")


class CorrelationResponse(BaseModel):
    """Correlation analysis response"""
    correlation_matrix: Dict[str, Any]
    significant_pairs: List[Dict[str, Any]]
    analysis: str


class AnomalyRequest(BaseModel):
    """Anomaly detection request"""
    countries: Optional[List[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    sensitivity: float = Field(default=0.05, ge=0.01, le=0.1)


class AnomalyResponse(BaseModel):
    """Anomaly detection response"""
    anomalies: List[Dict[str, Any]]
    count: int
    countries_analyzed: int
    analysis: str


class CountryInfo(BaseModel):
    """Country information"""
    name: str
    data_start: date
    data_end: date
    total_records: int
    mean_sentiment: float
    std_sentiment: float


class DateRangeResponse(BaseModel):
    """Date range response"""
    start_date: date
    end_date: date
    total_days: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, bool]


class SentimentDataPoint(BaseModel):
    """Single sentiment data point"""
    date: date
    country: str
    sentiment: float
    
    
class TextChunk(BaseModel):
    """Text chunk for RAG"""
    chunk_id: str
    text: str
    metadata: Dict[str, Any]
    chunk_type: str  # daily, weekly, monthly, country_summary, event
