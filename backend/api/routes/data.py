"""
Data query endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
from loguru import logger

from backend.models.schemas import CountryInfo, DateRangeResponse
from backend.services.data_loader import SentimentDataLoader

router = APIRouter(prefix="/api/data", tags=["data"])

# Initialize data loader
data_loader = None


def get_data_loader():
    """Get or initialize data loader"""
    global data_loader
    if data_loader is None:
        data_loader = SentimentDataLoader()
        data_loader.load_csv()
        data_loader.generate_metadata()
    return data_loader


@router.get("/countries", response_model=List[CountryInfo])
async def get_countries():
    """
    Get list of all countries with data
    
    Returns metadata for each country including date range and basic statistics.
    """
    try:
        loader = get_data_loader()
        
        countries = []
        for country, stats in loader.metadata['country_stats'].items():
            countries.append(CountryInfo(
                name=country,
                data_start=stats['start_date'],
                data_end=stats['end_date'],
                total_records=stats['total_records'],
                mean_sentiment=stats['mean'],
                std_sentiment=stats['std']
            ))
        
        return countries
        
    except Exception as e:
        logger.error(f"Error getting countries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/date-range", response_model=DateRangeResponse)
async def get_date_range():
    """
    Get the date range covered by the dataset
    
    Returns the earliest and latest dates available.
    """
    try:
        loader = get_data_loader()
        
        return DateRangeResponse(
            start_date=loader.metadata['start_date'],
            end_date=loader.metadata['end_date'],
            total_days=loader.metadata['total_rows']
        )
        
    except Exception as e:
        logger.error(f"Error getting date range: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/countries/{country}")
async def get_country_data(country: str, start_date: str = None, end_date: str = None):
    """
    Get data for a specific country
    
    Optionally filter by date range.
    """
    try:
        loader = get_data_loader()
        
        data = loader.get_country_data(country, start_date, end_date)
        
        # Convert to list of dicts
        records = []
        for _, row in data.iterrows():
            records.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'sentiment': float(row['sentiment'])
            })
        
        return {
            'country': country,
            'records': records,
            'count': len(records)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting country data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
