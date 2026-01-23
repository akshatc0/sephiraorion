"""
Data loading and preprocessing for sentiment data
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
import json
from loguru import logger
from backend.core.config import get_settings
from backend.utils.chunking import SentimentChunker


class SentimentDataLoader:
    """Load and process sentiment data"""
    
    def __init__(self, csv_path: str = None):
        self.settings = get_settings()
        self.csv_path = csv_path or self.settings.data_path
        self.df = None
        self.metadata = {}
        
    def load_csv(self) -> pd.DataFrame:
        """Load sentiment data from CSV"""
        logger.info(f"Loading data from {self.csv_path}")
        
        # Read CSV
        df = pd.read_csv(self.csv_path)
        
        # Drop the first unnamed column if it exists (index column)
        if df.columns[0].startswith('Unnamed'):
            df = df.drop(df.columns[0], axis=1)
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)
        
        self.df = df
        logger.info(f"Loaded {len(df)} rows from {df['date'].min()} to {df['date'].max()}")
        
        return df
    
    def generate_metadata(self) -> Dict[str, Any]:
        """Generate metadata about the dataset"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_csv() first.")
        
        countries = [col for col in self.df.columns if col != 'date']
        
        metadata = {
            'total_rows': len(self.df),
            'start_date': self.df['date'].min().strftime('%Y-%m-%d'),
            'end_date': self.df['date'].max().strftime('%Y-%m-%d'),
            'countries': countries,
            'total_countries': len(countries),
            'country_stats': {}
        }
        
        # Generate per-country statistics
        for country in countries:
            values = self.df[country].dropna()
            
            if len(values) > 0:
                metadata['country_stats'][country] = {
                    'total_records': int(len(values)),
                    'start_date': self.df.loc[values.index[0], 'date'].strftime('%Y-%m-%d'),
                    'end_date': self.df.loc[values.index[-1], 'date'].strftime('%Y-%m-%d'),
                    'mean': float(values.mean()),
                    'std': float(values.std()),
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'median': float(values.median())
                }
        
        self.metadata = metadata
        logger.info(f"Generated metadata for {metadata['total_countries']} countries")
        
        return metadata
    
    def create_time_series_format(self) -> pd.DataFrame:
        """Convert to long format for time series analysis"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_csv() first.")
        
        # Melt the dataframe to long format
        df_long = self.df.melt(
            id_vars=['date'],
            var_name='country',
            value_name='sentiment'
        )
        
        # Remove null values
        df_long = df_long.dropna()
        
        # Sort by country and date
        df_long = df_long.sort_values(['country', 'date']).reset_index(drop=True)
        
        logger.info(f"Created time series format with {len(df_long)} records")
        
        return df_long
    
    def create_text_chunks(self) -> List[Dict[str, Any]]:
        """Create text chunks for RAG"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_csv() first.")
        
        # Use chunker to create all types of chunks
        chunker = SentimentChunker(self.df.copy())
        chunks = chunker.create_all_chunks()
        
        logger.info(f"Created {len(chunks)} text chunks")
        
        return chunks
    
    def save_processed_data(self, output_dir: str = None):
        """Save processed data to disk"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_csv() first.")
        
        output_dir = output_dir or self.settings.processed_data_path
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save time series format
        ts_df = self.create_time_series_format()
        ts_path = output_path / "sentiment_timeseries.parquet"
        ts_df.to_parquet(ts_path, index=False)
        logger.info(f"Saved time series data to {ts_path}")
        
        # Save original wide format
        wide_path = output_path / "sentiment_wide.parquet"
        self.df.to_parquet(wide_path, index=False)
        logger.info(f"Saved wide format data to {wide_path}")
        
        # Save metadata
        if not self.metadata:
            self.generate_metadata()
        
        metadata_path = output_path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        logger.info(f"Saved metadata to {metadata_path}")
        
        # Save text chunks
        chunks = self.create_text_chunks()
        chunks_path = output_path / "text_chunks.json"
        with open(chunks_path, 'w') as f:
            json.dump(chunks, f, indent=2)
        logger.info(f"Saved {len(chunks)} text chunks to {chunks_path}")
        
        return {
            'timeseries_path': str(ts_path),
            'wide_path': str(wide_path),
            'metadata_path': str(metadata_path),
            'chunks_path': str(chunks_path)
        }
    
    def get_country_data(self, country: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Get data for a specific country and date range"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_csv() first.")
        
        if country not in self.df.columns:
            raise ValueError(f"Country '{country}' not found in dataset")
        
        # Filter by date range
        df_filtered = self.df.copy()
        
        if start_date:
            df_filtered = df_filtered[df_filtered['date'] >= pd.to_datetime(start_date)]
        
        if end_date:
            df_filtered = df_filtered[df_filtered['date'] <= pd.to_datetime(end_date)]
        
        # Return date and country columns
        result = df_filtered[['date', country]].dropna()
        result = result.rename(columns={country: 'sentiment'})
        
        return result
    
    def get_multiple_countries(self, countries: List[str], start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Get data for multiple countries"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_csv() first.")
        
        # Filter by date range
        df_filtered = self.df.copy()
        
        if start_date:
            df_filtered = df_filtered[df_filtered['date'] >= pd.to_datetime(start_date)]
        
        if end_date:
            df_filtered = df_filtered[df_filtered['date'] <= pd.to_datetime(end_date)]
        
        # Select date column and requested countries
        cols = ['date'] + [c for c in countries if c in df_filtered.columns]
        
        return df_filtered[cols]


def main():
    """Main function to load and process data"""
    logger.info("Starting data processing...")
    
    loader = SentimentDataLoader()
    
    # Load data
    loader.load_csv()
    
    # Generate metadata
    loader.generate_metadata()
    
    # Save processed data
    paths = loader.save_processed_data()
    
    logger.info("Data processing complete!")
    logger.info(f"Processed files saved to: {paths}")
    
    # Print summary
    print("\n" + "="*50)
    print("Data Processing Summary")
    print("="*50)
    print(f"Total rows: {loader.metadata['total_rows']}")
    print(f"Date range: {loader.metadata['start_date']} to {loader.metadata['end_date']}")
    print(f"Countries: {loader.metadata['total_countries']}")
    print(f"Sample countries: {', '.join(loader.metadata['countries'][:5])}")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
