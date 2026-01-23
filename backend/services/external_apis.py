"""
External API integrations for financial, news, and economic data
"""
import requests
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger
import yfinance as yf
from backend.core.config import get_settings


class ExternalAPIService:
    """Service for integrating external data sources"""
    
    def __init__(self):
        self.settings = get_settings()
        
    def get_financial_data(
        self,
        symbol: str = "^GSPC",  # S&P 500 by default
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get financial market data using yfinance
        
        Args:
            symbol: Stock/index symbol (e.g., ^GSPC for S&P 500)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dict with financial data
        """
        try:
            logger.info(f"Fetching financial data for {symbol}")
            
            # Set default dates if not provided
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            # Fetch data using yfinance
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                return {
                    'error': f'No data available for {symbol}',
                    'data': []
                }
            
            # Convert to list of dicts
            data = []
            for date, row in hist.iterrows():
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
            
            # Get ticker info
            info = ticker.info
            
            return {
                'symbol': symbol,
                'data': data,
                'info': {
                    'name': info.get('longName', symbol),
                    'currency': info.get('currency', 'USD'),
                    'exchange': info.get('exchange', 'Unknown')
                },
                'start_date': start_date,
                'end_date': end_date,
                'records': len(data)
            }
            
        except Exception as e:
            logger.error(f"Error fetching financial data: {e}")
            return {
                'error': str(e),
                'data': []
            }
    
    def get_news(
        self,
        query: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        language: str = 'en',
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Get news articles using NewsAPI
        
        Args:
            query: Search query
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            language: Language code
            page_size: Number of articles
            
        Returns:
            Dict with news articles
        """
        if not self.settings.news_api_key:
            return {
                'error': 'NewsAPI key not configured',
                'articles': []
            }
        
        try:
            logger.info(f"Fetching news for query: {query}")
            
            # Set default dates
            if not to_date:
                to_date = datetime.now().strftime('%Y-%m-%d')
            if not from_date:
                from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Build request
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': query,
                'from': from_date,
                'to': to_date,
                'language': language,
                'pageSize': page_size,
                'sortBy': 'relevancy',
                'apiKey': self.settings.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'ok':
                return {
                    'error': data.get('message', 'Unknown error'),
                    'articles': []
                }
            
            # Format articles
            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'title': article.get('title'),
                    'description': article.get('description'),
                    'source': article.get('source', {}).get('name'),
                    'url': article.get('url'),
                    'published_at': article.get('publishedAt'),
                    'author': article.get('author')
                })
            
            return {
                'query': query,
                'articles': articles,
                'total_results': data.get('totalResults', 0),
                'from_date': from_date,
                'to_date': to_date
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news: {e}")
            return {
                'error': str(e),
                'articles': []
            }
    
    def get_economic_indicators(
        self,
        series_id: str = 'GDP',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get economic indicators from FRED API
        
        Args:
            series_id: FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dict with economic data
        """
        if not self.settings.fred_api_key:
            return {
                'error': 'FRED API key not configured',
                'data': []
            }
        
        try:
            logger.info(f"Fetching FRED data for series: {series_id}")
            
            # Use fredapi library
            from fredapi import Fred
            fred = Fred(api_key=self.settings.fred_api_key)
            
            # Get series data
            if start_date and end_date:
                data = fred.get_series(
                    series_id,
                    observation_start=start_date,
                    observation_end=end_date
                )
            else:
                # Get last 10 years by default
                data = fred.get_series(series_id)
            
            # Convert to list of dicts
            records = []
            for date, value in data.items():
                if not pd.isna(value):
                    records.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'value': float(value)
                    })
            
            # Get series info
            info = fred.get_series_info(series_id)
            
            return {
                'series_id': series_id,
                'title': info['title'],
                'units': info.get('units', 'Unknown'),
                'frequency': info.get('frequency', 'Unknown'),
                'data': records,
                'records': len(records)
            }
            
        except Exception as e:
            logger.error(f"Error fetching FRED data: {e}")
            return {
                'error': str(e),
                'data': []
            }
    
    def correlate_with_sentiment(
        self,
        external_data: List[Dict[str, Any]],
        sentiment_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Correlate external data with sentiment data
        
        Args:
            external_data: List of external data points with 'date' and 'value'
            sentiment_data: List of sentiment data points with 'date' and 'sentiment'
            
        Returns:
            Dict with correlation analysis
        """
        try:
            import pandas as pd
            from scipy.stats import pearsonr
            
            # Convert to dataframes
            df_external = pd.DataFrame(external_data)
            df_sentiment = pd.DataFrame(sentiment_data)
            
            # Ensure date columns are datetime
            df_external['date'] = pd.to_datetime(df_external['date'])
            df_sentiment['date'] = pd.to_datetime(df_sentiment['date'])
            
            # Merge on date
            merged = pd.merge(df_external, df_sentiment, on='date', how='inner')
            
            if len(merged) < 10:
                return {
                    'error': 'Insufficient overlapping data points',
                    'correlation': None
                }
            
            # Calculate correlation
            corr, p_value = pearsonr(merged['value'], merged['sentiment'])
            
            return {
                'correlation': float(corr),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'data_points': len(merged),
                'interpretation': self._interpret_correlation(corr, p_value)
            }
            
        except Exception as e:
            logger.error(f"Error correlating data: {e}")
            return {
                'error': str(e),
                'correlation': None
            }
    
    def _interpret_correlation(self, corr: float, p_value: float) -> str:
        """Interpret correlation coefficient"""
        if p_value >= 0.05:
            return "No statistically significant correlation"
        
        abs_corr = abs(corr)
        strength = "weak" if abs_corr < 0.3 else "moderate" if abs_corr < 0.7 else "strong"
        direction = "positive" if corr > 0 else "negative"
        
        return f"Statistically significant {strength} {direction} correlation"


# Helper function to get common market indices
def get_market_indices() -> Dict[str, str]:
    """Get common market indices"""
    return {
        'S&P 500': '^GSPC',
        'Dow Jones': '^DJI',
        'NASDAQ': '^IXIC',
        'FTSE 100': '^FTSE',
        'DAX': '^GDAXI',
        'Nikkei 225': '^N225',
        'Hang Seng': '^HSI',
        'CAC 40': '^FCHI'
    }


# Helper function to get common FRED series
def get_fred_series() -> Dict[str, str]:
    """Get common FRED economic series"""
    return {
        'GDP': 'GDP',
        'Unemployment Rate': 'UNRATE',
        'Consumer Price Index': 'CPIAUCSL',
        'Federal Funds Rate': 'FEDFUNDS',
        'Industrial Production': 'INDPRO',
        'Consumer Sentiment': 'UMCSENT',
        'Retail Sales': 'RSXFS',
        'Housing Starts': 'HOUST'
    }
