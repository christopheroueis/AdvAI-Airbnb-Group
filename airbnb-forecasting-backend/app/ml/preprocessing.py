"""
Data preprocessing pipeline for Airbnb forecasting.
Handles data loading, cleaning, feature engineering, and time series preparation.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class DataPipeline:
    """Main data preprocessing pipeline."""
    
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.quarterly_data = None
        self.time_series = None
        
    def load_quarterly_listings(self) -> pd.DataFrame:
        """Load and combine listings data from all quarters."""
        quarters = ['LA_2022.10-12', 'LA_2023.1-3', 'LA_2023.4-6', 'LA_2023.7-9']
        quarter_labels = ['2022Q4', '2023Q1', '2023Q2', '2023Q3']
        
        dfs = []
        for q_dir, q_label in zip(quarters, quarter_labels):
            filepath = self.data_dir.parent.parent / q_dir / 'listings.csv'
            if not filepath.exists():
                print(f"Warning: {filepath} not found")
                continue
                
            df = pd.read_csv(filepath)
            df['source'] = q_label
            dfs.append(df)
        
        combined = pd.concat(dfs, ignore_index=True)
        print(f"Loaded {len(combined)} listings across {len(dfs)} quarters")
        return combined
    
    def prepare_time_series_volume(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare time series for listing volume forecasting."""
        # Aggregate by quarter
        ts = df.groupby('source').agg({
            'id': 'count',  # total listings
        }).reset_index()
        
        ts.columns = ['quarter', 'total_listings']
        
        # Sort by quarter
        quarter_order = ['2022Q4', '2023Q1', '2023Q2', '2023Q3']
        ts['quarter'] = pd.Categorical(ts['quarter'], categories=quarter_order, ordered=True)
        ts = ts.sort_values('quarter').reset_index(drop=True)
        
        # Add time index
        ts['time_index'] = range(len(ts))
        
        return ts
    
    def prepare_time_series_price(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare time series for price forecasting."""
        # Remove outliers (prices > 99th percentile)
        price_99 = df['price'].quantile(0.99)
        df_clean = df[df['price'] <= price_99].copy()
        
        ts = df_clean.groupby('source').agg({
            'price': 'mean',
        }).reset_index()
        
        ts.columns = ['quarter', 'avg_price']
        
        quarter_order = ['2022Q4', '2023Q1', '2023Q2', '2023Q3']
        ts['quarter'] = pd.Categorical(ts['quarter'], categories=quarter_order, ordered=True)
        ts = ts.sort_values('quarter').reset_index(drop=True)
        ts['time_index'] = range(len(ts))
        
        return ts
    
    def prepare_time_series_multivariate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare multivariate time series for VAR/VECM models."""
        # Clean price
        price_99 = df['price'].quantile(0.99)
        df_clean = df[df['price'] <= price_99].copy()
        
        ts = df_clean.groupby('source').agg({
            'id': 'count',
            'price': 'mean',
            'availability_365': 'mean',
            'number_of_reviews_ltm': 'sum',
            'reviews_per_month': 'mean',
        }).reset_index()
        
        ts.columns = ['quarter', 'total_listings', 'avg_price', 
                      'avg_availability', 'total_reviews_ltm', 'avg_reviews_per_month']
        
        # Sort
        quarter_order = ['2022Q4', '2023Q1', '2023Q2', '2023Q3']
        ts['quarter'] = pd.Categorical(ts['quarter'], categories=quarter_order, ordered=True)
        ts = ts.sort_values('quarter').reset_index(drop=True)
        ts['time_index'] = range(len(ts))
        
        # Calculate derived metrics
        ts['occupancy_rate'] = 1 - (ts['avg_availability'] / 365)
        ts['review_rate'] = ts['total_reviews_ltm'] / ts['total_listings']
        
        return ts
    
    def engineer_features_ml(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for ML models (XGBoost, Random Forest)."""
        df = df.copy()
        
        # Parse amenities count
        if 'amenities' in df.columns:
            df['amenities_count'] = df['amenities'].fillna('[]').apply(
                lambda x: len(eval(x)) if isinstance(x, str) else 0
            )
        
        # Binary amenity flags
        if 'amenities' in df.columns:
            df['has_wifi'] = df['amenities'].fillna('').str.contains('Wifi|wifi', case=False).astype(int)
            df['has_kitchen'] = df['amenities'].fillna('').str.contains('Kitchen|kitchen', case=False).astype(int)
            df['has_parking'] = df['amenities'].fillna('').str.contains('parking|Parking', case=False).astype(int)
        
        # Temporal features
        quarter_map = {'2022Q4': 0, '2023Q1': 1, '2023Q2': 2, '2023Q3': 3}
        df['quarter_num'] = df['source'].map(quarter_map)
        df['is_summer'] = df['source'].isin(['2023Q2', '2023Q3']).astype(int)
        
        # Location density (neighborhood listing count)
        if 'neighbourhood_cleansed' in df.columns:
            neighborhood_counts = df.groupby('neighbourhood_cleansed').size()
            df['neighborhood_density'] = df['neighbourhood_cleansed'].map(neighborhood_counts)
        
        # Host features
        df['is_superhost'] = (df['host_is_superhost'] == 't').astype(int) if 'host_is_superhost' in df.columns else 0
        df['multi_listing_host'] = (df['calculated_host_listings_count'] > 1).astype(int) if 'calculated_host_listings_count' in df.columns else 0
        
        return df
    
    def create_train_test_split(self, ts: pd.DataFrame, 
                                 test_size: int = 1) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split time series into train/test with temporal ordering."""
        # Last 'test_size' quarters for testing
        train = ts.iloc[:-test_size].copy()
        test = ts.iloc[-test_size:].copy()
        
        print(f"Train: {len(train)} quarters, Test: {len(test)} quarters")
        return train, test
    
    def run_full_pipeline(self) -> Dict[str, pd.DataFrame]:
        """Run complete data preprocessing pipeline."""
        print("=" * 60)
        print("Starting Data Preprocessing Pipeline")
        print("=" * 60)
        
        # Load data
        print("\n1. Loading quarterly listings data...")
        listings = self.load_quarterly_listings()
        
        # Prepare different time series
        print("\n2. Preparing time series datasets...")
        
        ts_volume = self.prepare_time_series_volume(listings)
        print(f"   - Volume time series: {ts_volume.shape}")
        
        ts_price = self.prepare_time_series_price(listings)
        print(f"   - Price time series: {ts_price.shape}")
        
        ts_multivariate = self.prepare_time_series_multivariate(listings)
        print(f"   - Multivariate time series: {ts_multivariate.shape}")
        
        # Engineer features for ML
        print("\n3. Engineering features for ML models...")
        listings_ml = self.engineer_features_ml(listings)
        print(f"   - ML features dataset: {listings_ml.shape}")
        
        # Train/test split
        print("\n4. Creating train/test splits...")
        train_volume, test_volume = self.create_train_test_split(ts_volume, test_size=1)
        train_multivar, test_multivar = self.create_train_test_split(ts_multivariate, test_size=1)
        
        print("\n" + "=" * 60)
        print("Pipeline Complete!")
        print("=" * 60)
        
        return {
            'listings_raw': listings,
            'listings_ml': listings_ml,
            'ts_volume': ts_volume,
            'ts_price': ts_price,
            'ts_multivariate': ts_multivariate,
            'train_volume': train_volume,
            'test_volume': test_volume,
            'train_multivar': train_multivar,
            'test_multivar': test_multivar,
        }


if __name__ == "__main__":
    # Test the pipeline
    pipeline = DataPipeline(data_dir="../../../LA_2022.10-2023.9")
    results = pipeline.run_full_pipeline()
    
    # Display sample results
    print("\n" + "=" * 60)
    print("Sample Data:")
    print("=" * 60)
    print("\nVolume Time Series:")
    print(results['ts_volume'])
    
    print("\nMultivariate Time Series:")
    print(results['ts_multivariate'])
