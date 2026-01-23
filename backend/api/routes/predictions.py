"""
Prediction endpoints for forecasting, trends, correlations, and anomalies
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from loguru import logger

from backend.models.schemas import (
    ForecastRequest, ForecastResponse,
    TrendRequest, TrendResponse,
    CorrelationRequest, CorrelationResponse,
    AnomalyRequest, AnomalyResponse
)
from backend.models.predictor import SentimentPredictor
from backend.services.llm_client import LLMClient

router = APIRouter(prefix="/api/predict", tags=["predictions"])

# Initialize predictor and LLM client
predictor = None
llm_client = None


def get_predictor():
    """Get or initialize predictor"""
    global predictor
    if predictor is None:
        predictor = SentimentPredictor()
    return predictor


def get_llm_client():
    """Get or initialize LLM client"""
    global llm_client
    if llm_client is None:
        llm_client = LLMClient()
    return llm_client


@router.post("/forecast", response_model=ForecastResponse)
async def forecast(request: ForecastRequest):
    """
    Generate sentiment forecast for a country
    
    Uses Prophet model to forecast future sentiment values with confidence intervals.
    """
    try:
        pred = get_predictor()
        result = pred.forecast_sentiment(
            country=request.country,
            days=request.days,
            confidence_level=request.confidence_level
        )
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return ForecastResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trends", response_model=TrendResponse)
async def analyze_trends(request: TrendRequest):
    """
    Analyze sentiment trends for multiple countries
    
    Calculates moving averages, momentum, and trend direction.
    """
    try:
        pred = get_predictor()
        llm = get_llm_client()
        
        result = pred.analyze_trends(
            countries=request.countries,
            start_date=request.start_date.strftime('%Y-%m-%d') if request.start_date else None,
            end_date=request.end_date.strftime('%Y-%m-%d') if request.end_date else None,
            window=request.window
        )
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        # Generate analysis using LLM
        summary = f"Trend Analysis Results:\n"
        for country, trend_data in result['trends'].items():
            summary += f"\n{country}:\n"
            summary += f"  Current: {trend_data['current_value']:.2f}\n"
            summary += f"  Direction: {trend_data['trend_direction']}\n"
            summary += f"  Strength: {trend_data['trend_strength']:.2f}\n"
            summary += f"  Volatility: {trend_data['volatility']:.2f}\n"
        
        analysis = llm.generate_analysis(summary, 'trend')
        
        return TrendResponse(
            trends=result['trends'],
            analysis=analysis,
            charts=None  # Could add chart data here
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/correlations", response_model=CorrelationResponse)
async def calculate_correlations(request: CorrelationRequest):
    """
    Calculate correlations between countries
    
    Identifies relationships and patterns across different countries' sentiment data.
    """
    try:
        pred = get_predictor()
        llm = get_llm_client()
        
        result = pred.calculate_correlations(
            countries=request.countries,
            start_date=request.start_date.strftime('%Y-%m-%d') if request.start_date else None,
            end_date=request.end_date.strftime('%Y-%m-%d') if request.end_date else None,
            method=request.method
        )
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        # Generate analysis using LLM
        summary = f"Correlation Analysis Results ({request.method}):\n"
        summary += f"Countries analyzed: {result['countries_analyzed']}\n\n"
        summary += "Top correlations:\n"
        for pair in result['significant_pairs'][:10]:
            summary += f"{pair['country1']} ↔ {pair['country2']}: {pair['correlation']:.3f} ({pair['strength']})\n"
        
        analysis = llm.generate_analysis(summary, 'correlation')
        
        return CorrelationResponse(
            correlation_matrix=result['correlation_matrix'],
            significant_pairs=result['significant_pairs'],
            analysis=analysis
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating correlations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/anomalies", response_model=AnomalyResponse)
async def detect_anomalies(request: AnomalyRequest):
    """
    Detect anomalies in sentiment data
    
    Uses statistical methods and ML to identify unusual patterns.
    """
    try:
        pred = get_predictor()
        llm = get_llm_client()
        
        result = pred.detect_anomalies(
            countries=request.countries,
            start_date=request.start_date.strftime('%Y-%m-%d') if request.start_date else None,
            end_date=request.end_date.strftime('%Y-%m-%d') if request.end_date else None,
            sensitivity=request.sensitivity
        )
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        # Generate analysis using LLM
        summary = f"Anomaly Detection Results:\n"
        summary += f"Total anomalies detected: {result['count']}\n"
        summary += f"Sensitivity: {result['sensitivity']}\n\n"
        summary += "Recent anomalies:\n"
        for anomaly in result['anomalies'][:10]:
            summary += f"{anomaly['country']} on {anomaly['date']}: {anomaly['sentiment']:.2f} "
            summary += f"({anomaly['type']}, {anomaly['severity']})\n"
        
        analysis = llm.generate_analysis(summary, 'anomaly')
        
        return AnomalyResponse(
            anomalies=result['anomalies'],
            count=result['count'],
            countries_analyzed=result['countries_analyzed'],
            analysis=analysis
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))
