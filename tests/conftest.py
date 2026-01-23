"""
Pytest configuration and fixtures
"""
import pytest
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def test_config():
    """Test configuration"""
    return {
        'test_data_path': 'data/raw/all_indexes_beta.csv',
        'test_api_url': 'http://localhost:8000'
    }


@pytest.fixture
def sample_sentiment_data():
    """Sample sentiment data for testing"""
    import pandas as pd
    
    return pd.DataFrame({
        'date': pd.date_range('2020-01-01', periods=100),
        'United States': [6.5 + i*0.001 for i in range(100)],
        'United Kingdom': [7.0 + i*0.001 for i in range(100)],
        'Germany': [6.8 + i*0.001 for i in range(100)]
    })
