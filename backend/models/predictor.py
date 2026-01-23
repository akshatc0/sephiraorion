"""
Prediction models for sentiment forecasting, trend analysis, correlations, and anomalies
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger
from prophet import Prophet
from sklearn.ensemble import IsolationForest
from scipy.stats import pearsonr, spearmanr
import warnings
warnings.filterwarnings('ignore')

from backend.core.config import get_settings
from backend.services.data_loader import SentimentDataLoader


class SentimentPredictor:
    """Prediction models for sentiment analysis"""
    
    def __init__(self):
        self.settings = get_settings()
        self.data_loader = SentimentDataLoader()
        self.data_loader.load_csv()
        
    def forecast_sentiment(
        self,
        country: str,
        days: int = 30,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Forecast sentiment for a country using Prophet
        
        Args:
            country: Country name
            days: Number of days to forecast
            confidence_level: Confidence interval level
            
        Returns:
            Dict with forecasts and model info
        """
        logger.info(f"Forecasting {days} days for {country}")
        
        try:
            # Get country data
            country_data = self.data_loader.get_country_data(country)
            
            if len(country_data) < 30:
                return {
                    'error': f'Insufficient data for {country}',
                    'forecasts': [],
                    'model_info': {}
                }
            
            # Prepare data for Prophet
            df_prophet = pd.DataFrame({
                'ds': country_data['date'],
                'y': country_data['sentiment']
            })
            
            # Train Prophet model
            # Suppress Prophet verbose output
            import logging
            logging.getLogger('cmdstanpy').setLevel(logging.ERROR)
            logging.getLogger('prophet').setLevel(logging.ERROR)
            
            model = Prophet(
                interval_width=confidence_level,
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                changepoint_prior_scale=0.05
            )
            
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model.fit(df_prophet)
            
            # Make future dataframe
            future = model.make_future_dataframe(periods=days)
            forecast = model.predict(future)
            
            # Extract forecast data (only future dates)
            forecast_data = forecast.tail(days)
            
            forecasts = []
            for _, row in forecast_data.iterrows():
                forecasts.append({
                    'date': row['ds'].strftime('%Y-%m-%d'),
                    'predicted_sentiment': float(row['yhat']),
                    'lower_bound': float(row['yhat_lower']),
                    'upper_bound': float(row['yhat_upper']),
                    'trend': float(row['trend'])
                })
            
            # Calculate simple accuracy metrics on historical data
            historical_pred = forecast[:-days]
            actual = df_prophet['y'].values
            predicted = historical_pred['yhat'].values[:len(actual)]
            
            mape = np.mean(np.abs((actual - predicted) / actual)) * 100
            rmse = np.sqrt(np.mean((actual - predicted) ** 2))
            
            model_info = {
                'model': 'Prophet',
                'training_samples': len(df_prophet),
                'forecast_days': days,
                'confidence_level': confidence_level,
                'last_actual_date': country_data['date'].max().strftime('%Y-%m-%d'),
                'last_actual_value': float(country_data['sentiment'].iloc[-1])
            }
            
            accuracy_metrics = {
                'mape': float(mape),
                'rmse': float(rmse)
            }
            
            return {
                'country': country,
                'forecasts': forecasts,
                'model_info': model_info,
                'accuracy_metrics': accuracy_metrics
            }
            
        except Exception as e:
            logger.error(f"Error forecasting for {country}: {e}")
            return {
                'error': str(e),
                'forecasts': [],
                'model_info': {}
            }
    
    def analyze_trends(
        self,
        countries: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        window: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze trends for multiple countries
        
        Args:
            countries: List of country names
            start_date: Start date for analysis
            end_date: End date for analysis
            window: Moving average window
            
        Returns:
            Dict with trend analysis
        """
        logger.info(f"Analyzing trends for {len(countries)} countries")
        
        try:
            # Get data for multiple countries
            df = self.data_loader.get_multiple_countries(countries, start_date, end_date)
            
            trends = {}
            
            for country in countries:
                if country not in df.columns:
                    continue
                
                country_series = df[['date', country]].dropna()
                
                if len(country_series) < window:
                    continue
                
                # Calculate moving averages
                country_series['ma_7'] = country_series[country].rolling(window=7).mean()
                country_series['ma_30'] = country_series[country].rolling(window=30).mean()
                
                # Calculate momentum (rate of change)
                country_series['momentum'] = country_series[country].diff()
                
                # Determine trend direction
                recent_values = country_series[country].tail(window)
                if len(recent_values) > 1:
                    trend_direction = 'increasing' if recent_values.iloc[-1] > recent_values.iloc[0] else 'decreasing'
                    
                    # Calculate trend strength (correlation with time)
                    time_index = np.arange(len(recent_values))
                    corr, _ = pearsonr(time_index, recent_values.values)
                    trend_strength = abs(corr)
                else:
                    trend_direction = 'stable'
                    trend_strength = 0.0
                
                # Find turning points (local maxima/minima)
                turning_points = self._find_turning_points(country_series[country])
                
                trends[country] = {
                    'current_value': float(country_series[country].iloc[-1]),
                    'ma_7': float(country_series['ma_7'].iloc[-1]) if not pd.isna(country_series['ma_7'].iloc[-1]) else None,
                    'ma_30': float(country_series['ma_30'].iloc[-1]) if not pd.isna(country_series['ma_30'].iloc[-1]) else None,
                    'trend_direction': trend_direction,
                    'trend_strength': float(trend_strength),
                    'momentum': float(country_series['momentum'].iloc[-1]) if not pd.isna(country_series['momentum'].iloc[-1]) else 0.0,
                    'turning_points': turning_points[-3:] if turning_points else [],  # Last 3 turning points
                    'volatility': float(country_series[country].std())
                }
            
            return {
                'trends': trends,
                'analysis_period': {
                    'start': df['date'].min().strftime('%Y-%m-%d'),
                    'end': df['date'].max().strftime('%Y-%m-%d'),
                    'window': window
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {
                'error': str(e),
                'trends': {}
            }
    
    def calculate_correlations(
        self,
        countries: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        method: str = 'pearson'
    ) -> Dict[str, Any]:
        """
        Calculate correlation matrix for countries
        
        Args:
            countries: List of countries (None for all)
            start_date: Start date
            end_date: End date
            method: Correlation method ('pearson' or 'spearman')
            
        Returns:
            Dict with correlation matrix and analysis
        """
        logger.info(f"Calculating correlations using {method} method")
        
        try:
            # Get all countries if not specified
            if countries is None:
                countries = [col for col in self.data_loader.df.columns if col != 'date']
            
            # Get data
            df = self.data_loader.get_multiple_countries(countries, start_date, end_date)
            
            # Calculate correlation matrix
            numeric_df = df.select_dtypes(include=[np.number])
            
            if method == 'pearson':
                corr_matrix = numeric_df.corr(method='pearson')
            else:
                corr_matrix = numeric_df.corr(method='spearman')
            
            # Convert to dict
            corr_dict = corr_matrix.to_dict()
            
            # Find significant pairs (high correlation)
            significant_pairs = []
            threshold = 0.7
            
            for i, country1 in enumerate(corr_matrix.columns):
                for j, country2 in enumerate(corr_matrix.columns):
                    if i < j:  # Avoid duplicates and self-correlation
                        corr_value = corr_matrix.iloc[i, j]
                        if abs(corr_value) >= threshold:
                            significant_pairs.append({
                                'country1': country1,
                                'country2': country2,
                                'correlation': float(corr_value),
                                'strength': 'strong' if abs(corr_value) >= 0.9 else 'moderate'
                            })
            
            # Sort by absolute correlation
            significant_pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)
            
            return {
                'correlation_matrix': corr_dict,
                'significant_pairs': significant_pairs[:20],  # Top 20
                'method': method,
                'countries_analyzed': len(corr_matrix.columns),
                'analysis_period': {
                    'start': df['date'].min().strftime('%Y-%m-%d'),
                    'end': df['date'].max().strftime('%Y-%m-%d')
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating correlations: {e}")
            return {
                'error': str(e),
                'correlation_matrix': {},
                'significant_pairs': []
            }
    
    def detect_anomalies(
        self,
        countries: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        sensitivity: float = 0.05
    ) -> Dict[str, Any]:
        """
        Detect anomalies in sentiment data
        
        Args:
            countries: List of countries (None for all)
            start_date: Start date
            end_date: End date
            sensitivity: Contamination parameter (0.01-0.1)
            
        Returns:
            Dict with detected anomalies
        """
        logger.info(f"Detecting anomalies with sensitivity {sensitivity}")
        
        try:
            # Get all countries if not specified
            if countries is None:
                countries = [col for col in self.data_loader.df.columns if col != 'date'][:10]  # Limit to 10
            
            anomalies = []
            
            for country in countries:
                country_data = self.data_loader.get_country_data(country, start_date, end_date)
                
                if len(country_data) < 30:
                    continue
                
                # Method 1: Statistical outliers (Z-score)
                mean = country_data['sentiment'].mean()
                std = country_data['sentiment'].std()
                z_scores = (country_data['sentiment'] - mean) / std
                
                statistical_anomalies = country_data[np.abs(z_scores) > 3]
                
                for idx, row in statistical_anomalies.iterrows():
                    anomalies.append({
                        'country': country,
                        'date': row['date'].strftime('%Y-%m-%d'),
                        'sentiment': float(row['sentiment']),
                        'z_score': float(z_scores.loc[idx]),
                        'type': 'statistical',
                        'severity': 'high' if abs(z_scores.loc[idx]) > 4 else 'moderate'
                    })
                
                # Method 2: Isolation Forest
                if len(country_data) >= 100:
                    X = country_data['sentiment'].values.reshape(-1, 1)
                    
                    iso_forest = IsolationForest(
                        contamination=sensitivity,
                        random_state=42
                    )
                    predictions = iso_forest.fit_predict(X)
                    
                    # Get anomalies (prediction = -1)
                    ml_anomalies = country_data[predictions == -1]
                    
                    for idx, row in ml_anomalies.iterrows():
                        # Avoid duplicates
                        if idx not in statistical_anomalies.index:
                            anomalies.append({
                                'country': country,
                                'date': row['date'].strftime('%Y-%m-%d'),
                                'sentiment': float(row['sentiment']),
                                'type': 'ml_based',
                                'severity': 'moderate'
                            })
            
            # Sort by date (most recent first)
            anomalies.sort(key=lambda x: x['date'], reverse=True)
            
            return {
                'anomalies': anomalies[:50],  # Return top 50
                'count': len(anomalies),
                'countries_analyzed': len(countries),
                'sensitivity': sensitivity
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return {
                'error': str(e),
                'anomalies': [],
                'countries_analyzed': 0,
                'count': 0
            }
    
    def _find_turning_points(self, series: pd.Series, window: int = 5) -> List[Dict[str, Any]]:
        """Find local maxima and minima in time series"""
        turning_points = []
        
        for i in range(window, len(series) - window):
            window_data = series.iloc[i-window:i+window+1]
            current = series.iloc[i]
            
            if current == window_data.max():
                turning_points.append({
                    'type': 'peak',
                    'index': int(i),
                    'value': float(current)
                })
            elif current == window_data.min():
                turning_points.append({
                    'type': 'trough',
                    'index': int(i),
                    'value': float(current)
                })
        
        return turning_points
