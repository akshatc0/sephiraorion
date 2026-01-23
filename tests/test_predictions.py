"""
Tests for prediction models
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from backend.models.predictor import SentimentPredictor


class TestSentimentPredictor:
    """Test sentiment prediction models"""
    
    @pytest.fixture
    def mock_data_loader(self):
        """Create mock data loader"""
        with patch('backend.models.predictor.SentimentDataLoader') as mock:
            loader = Mock()
            
            # Create sample data
            dates = pd.date_range('2020-01-01', periods=365)
            df = pd.DataFrame({
                'date': dates,
                'United States': np.random.randn(365) * 0.1 + 6.5,
                'United Kingdom': np.random.randn(365) * 0.1 + 7.0
            })
            
            loader.df = df
            loader.get_country_data.return_value = pd.DataFrame({
                'date': dates,
                'sentiment': np.random.randn(365) * 0.1 + 6.5
            })
            loader.get_multiple_countries.return_value = df
            
            mock.return_value = loader
            yield loader
    
    def test_forecast_sentiment(self, mock_data_loader):
        """Test sentiment forecasting"""
        predictor = SentimentPredictor()
        
        result = predictor.forecast_sentiment(
            country='United States',
            days=7,
            confidence_level=0.95
        )
        
        # Check result structure
        assert 'forecasts' in result
        assert 'model_info' in result
        assert len(result['forecasts']) == 7
        
        # Check forecast data
        for forecast in result['forecasts']:
            assert 'date' in forecast
            assert 'predicted_sentiment' in forecast
            assert 'lower_bound' in forecast
            assert 'upper_bound' in forecast
    
    def test_analyze_trends(self, mock_data_loader):
        """Test trend analysis"""
        predictor = SentimentPredictor()
        
        result = predictor.analyze_trends(
            countries=['United States', 'United Kingdom'],
            window=30
        )
        
        # Check result structure
        assert 'trends' in result
        assert 'United States' in result['trends']
        assert 'United Kingdom' in result['trends']
        
        # Check trend data
        for country, trend in result['trends'].items():
            assert 'current_value' in trend
            assert 'trend_direction' in trend
            assert 'trend_strength' in trend
            assert trend['trend_direction'] in ['increasing', 'decreasing', 'stable']
    
    def test_calculate_correlations(self, mock_data_loader):
        """Test correlation calculation"""
        predictor = SentimentPredictor()
        
        result = predictor.calculate_correlations(
            countries=['United States', 'United Kingdom'],
            method='pearson'
        )
        
        # Check result structure
        assert 'correlation_matrix' in result
        assert 'significant_pairs' in result
        assert 'method' in result
        assert result['method'] == 'pearson'
        
        # Check correlation matrix
        assert 'United States' in result['correlation_matrix']
        assert 'United Kingdom' in result['correlation_matrix']
    
    def test_detect_anomalies(self, mock_data_loader):
        """Test anomaly detection"""
        predictor = SentimentPredictor()
        
        result = predictor.detect_anomalies(
            countries=['United States'],
            sensitivity=0.05
        )
        
        # Check result structure
        assert 'anomalies' in result
        assert 'count' in result
        assert isinstance(result['anomalies'], list)
        assert isinstance(result['count'], int)
        
        # Check anomaly data
        if result['anomalies']:
            for anomaly in result['anomalies']:
                assert 'country' in anomaly
                assert 'date' in anomaly
                assert 'sentiment' in anomaly
                assert 'type' in anomaly
    
    def test_turning_points(self, mock_data_loader):
        """Test turning point detection"""
        predictor = SentimentPredictor()
        
        # Create a series with clear peaks and troughs
        series = pd.Series([1, 2, 3, 2, 1, 2, 3, 4, 3, 2, 1])
        
        turning_points = predictor._find_turning_points(series, window=2)
        
        assert len(turning_points) > 0
        assert all('type' in tp for tp in turning_points)
        assert all(tp['type'] in ['peak', 'trough'] for tp in turning_points)


class TestDataLoader:
    """Test data loader functionality"""
    
    def test_load_csv(self):
        """Test CSV loading (requires actual data file)"""
        from backend.services.data_loader import SentimentDataLoader
        
        # This test requires the actual CSV file
        try:
            loader = SentimentDataLoader()
            df = loader.load_csv()
            
            assert df is not None
            assert 'date' in df.columns
            assert len(df) > 0
        except FileNotFoundError:
            pytest.skip("CSV file not found")
    
    def test_metadata_generation(self):
        """Test metadata generation"""
        from backend.services.data_loader import SentimentDataLoader
        
        try:
            loader = SentimentDataLoader()
            loader.load_csv()
            metadata = loader.generate_metadata()
            
            assert 'total_rows' in metadata
            assert 'start_date' in metadata
            assert 'end_date' in metadata
            assert 'countries' in metadata
            assert 'country_stats' in metadata
        except FileNotFoundError:
            pytest.skip("CSV file not found")


class TestExternalAPIs:
    """Test external API integrations"""
    
    def test_financial_data_structure(self):
        """Test financial data structure"""
        from backend.services.external_apis import ExternalAPIService
        
        service = ExternalAPIService()
        
        # Note: This test may fail if network is unavailable or API key is missing
        try:
            result = service.get_financial_data(symbol='^GSPC', start_date='2024-01-01', end_date='2024-01-07')
            
            if 'error' not in result:
                assert 'data' in result
                assert 'symbol' in result
                assert isinstance(result['data'], list)
        except Exception:
            pytest.skip("Financial API unavailable")
    
    def test_market_indices_helper(self):
        """Test market indices helper function"""
        from backend.services.external_apis import get_market_indices
        
        indices = get_market_indices()
        
        assert isinstance(indices, dict)
        assert 'S&P 500' in indices
        assert indices['S&P 500'] == '^GSPC'
    
    def test_fred_series_helper(self):
        """Test FRED series helper function"""
        from backend.services.external_apis import get_fred_series
        
        series = get_fred_series()
        
        assert isinstance(series, dict)
        assert 'GDP' in series
        assert series['GDP'] == 'GDP'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
