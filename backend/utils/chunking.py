"""
Chunking strategies for sentiment data
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


class SentimentChunker:
    """Create text chunks from sentiment data for RAG"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def create_daily_chunks(self) -> List[Dict[str, Any]]:
        """Create chunks for daily observations"""
        chunks = []
        
        for idx, row in self.df.iterrows():
            date_str = row['date']
            
            # Get non-null sentiment values for this day
            countries_data = []
            for col in self.df.columns:
                if col not in ['date'] and pd.notna(row[col]):
                    countries_data.append({
                        'country': col,
                        'sentiment': float(row[col])
                    })
            
            if not countries_data:
                continue
                
            # Create descriptive text
            text_parts = [f"On {date_str}, sentiment data:"]
            for cd in countries_data:
                text_parts.append(f"{cd['country']}: {cd['sentiment']:.2f}")
            
            text = " | ".join(text_parts)
            
            chunks.append({
                'chunk_id': f"daily_{date_str}",
                'text': text,
                'metadata': {
                    'date': str(date_str),
                    'countries': [cd['country'] for cd in countries_data],
                    'type': 'daily'
                },
                'chunk_type': 'daily'
            })
            
        return chunks
    
    def create_weekly_chunks(self) -> List[Dict[str, Any]]:
        """Create weekly aggregated chunks"""
        chunks = []
        
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['week'] = self.df['date'].dt.to_period('W')
        
        for week, group in self.df.groupby('week'):
            start_date = group['date'].min().strftime('%Y-%m-%d')
            end_date = group['date'].max().strftime('%Y-%m-%d')
            
            # Calculate weekly averages for each country
            text_parts = [f"Week of {start_date} to {end_date}:"]
            countries_data = {}
            
            for col in self.df.columns:
                if col not in ['date', 'week']:
                    values = group[col].dropna()
                    if len(values) > 0:
                        mean_val = values.mean()
                        std_val = values.std()
                        change = None
                        if len(values) > 1:
                            change = values.iloc[-1] - values.iloc[0]
                        
                        countries_data[col] = {
                            'mean': mean_val,
                            'std': std_val,
                            'change': change
                        }
                        
                        change_text = f"(change: {change:+.2f})" if change else ""
                        text_parts.append(
                            f"{col} avg: {mean_val:.2f} ±{std_val:.2f} {change_text}"
                        )
            
            if countries_data:
                chunks.append({
                    'chunk_id': f"weekly_{week}",
                    'text': " | ".join(text_parts),
                    'metadata': {
                        'start_date': str(start_date),
                        'end_date': str(end_date),
                        'countries': list(countries_data.keys()),
                        'type': 'weekly'
                    },
                    'chunk_type': 'weekly'
                })
        
        return chunks
    
    def create_monthly_chunks(self) -> List[Dict[str, Any]]:
        """Create monthly aggregated chunks"""
        chunks = []
        
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['month'] = self.df['date'].dt.to_period('M')
        
        for month, group in self.df.groupby('month'):
            month_str = str(month)
            
            # Calculate monthly statistics
            text_parts = [f"Month of {month_str}:"]
            countries_data = {}
            
            for col in self.df.columns:
                if col not in ['date', 'week', 'month']:
                    values = group[col].dropna()
                    if len(values) > 0:
                        mean_val = values.mean()
                        min_val = values.min()
                        max_val = values.max()
                        
                        countries_data[col] = {
                            'mean': mean_val,
                            'min': min_val,
                            'max': max_val
                        }
                        
                        text_parts.append(
                            f"{col}: mean={mean_val:.2f}, range=[{min_val:.2f}, {max_val:.2f}]"
                        )
            
            if countries_data:
                chunks.append({
                    'chunk_id': f"monthly_{month}",
                    'text': " | ".join(text_parts),
                    'metadata': {
                        'month': str(month_str),
                        'countries': list(countries_data.keys()),
                        'type': 'monthly'
                    },
                    'chunk_type': 'monthly'
                })
        
        return chunks
    
    def create_country_summary_chunks(self) -> List[Dict[str, Any]]:
        """Create summary chunks for each country"""
        chunks = []
        
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        for col in self.df.columns:
            if col not in ['date', 'week', 'month']:
                values = self.df[col].dropna()
                
                if len(values) == 0:
                    continue
                
                dates = self.df.loc[values.index, 'date']
                
                # Calculate statistics
                mean_val = values.mean()
                std_val = values.std()
                min_val = values.min()
                max_val = values.max()
                trend = "increasing" if values.iloc[-1] > values.iloc[0] else "decreasing"
                
                text = (
                    f"Country: {col}. "
                    f"Data available from {dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}. "
                    f"Overall statistics: mean={mean_val:.2f}, std={std_val:.2f}, "
                    f"min={min_val:.2f}, max={max_val:.2f}. "
                    f"Overall trend: {trend}. "
                    f"Total data points: {len(values)}."
                )
                
                chunks.append({
                    'chunk_id': f"country_summary_{col}",
                    'text': text,
                    'metadata': {
                        'country': col,
                        'start_date': str(dates.min().strftime('%Y-%m-%d')),
                        'end_date': str(dates.max().strftime('%Y-%m-%d')),
                        'mean': float(mean_val),
                        'std': float(std_val),
                        'type': 'country_summary'
                    },
                    'chunk_type': 'country_summary'
                })
        
        return chunks
    
    def create_anomaly_chunks(self, threshold: float = 3.0) -> List[Dict[str, Any]]:
        """Create chunks for significant anomalies (outliers)"""
        chunks = []
        
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        for col in self.df.columns:
            if col not in ['date', 'week', 'month']:
                values = self.df[col].dropna()
                
                if len(values) < 30:  # Need enough data for meaningful stats
                    continue
                
                # Calculate z-scores
                mean_val = values.mean()
                std_val = values.std()
                z_scores = (values - mean_val) / std_val
                
                # Find anomalies
                anomalies = values[np.abs(z_scores) > threshold]
                
                for idx in anomalies.index:
                    date_val = self.df.loc[idx, 'date']
                    sentiment_val = values.loc[idx]
                    z_score = z_scores.loc[idx]
                    
                    text = (
                        f"Anomaly detected for {col} on {date_val.strftime('%Y-%m-%d')}: "
                        f"sentiment value {sentiment_val:.2f} "
                        f"(z-score: {z_score:.2f}, significantly {'above' if z_score > 0 else 'below'} normal)."
                    )
                    
                    chunks.append({
                        'chunk_id': f"anomaly_{col}_{date_val.strftime('%Y%m%d')}",
                        'text': text,
                        'metadata': {
                            'country': col,
                            'date': str(date_val.strftime('%Y-%m-%d')),
                            'sentiment': float(sentiment_val),
                            'z_score': float(z_score),
                            'type': 'anomaly'
                        },
                        'chunk_type': 'event'
                    })
        
        return chunks
    
    def create_all_chunks(self) -> List[Dict[str, Any]]:
        """Create all types of chunks"""
        all_chunks = []
        
        # Create different types of chunks
        all_chunks.extend(self.create_daily_chunks())
        all_chunks.extend(self.create_weekly_chunks())
        all_chunks.extend(self.create_monthly_chunks())
        all_chunks.extend(self.create_country_summary_chunks())
        all_chunks.extend(self.create_anomaly_chunks())
        
        return all_chunks
