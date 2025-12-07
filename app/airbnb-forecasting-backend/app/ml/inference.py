"""
Model inference service for serving predictions.
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, List
import warnings
warnings.filterwarnings('ignore')


class ForecastService:
    """Service for loading models and serving predictions."""
    
    def __init__(self, models_dir: str = "data/models"):
        self.models_dir = Path(models_dir)
        self.models = {}
        self.load_all_models()
        
    def load_all_models(self):
        """Load all trained models."""
        model_files = {
            'sarima': 'sarima_volume.pkl',
            'prophet': 'prophet_volume.pkl',
            'lstm': 'lstm_volume.pkl',
            'xgboost_price': 'xgboost_price.pkl',
            'xgboost_occupancy': 'xgboost_occupancy.pkl',
            'ensemble': 'ensemble_volume.pkl',
        }
        
        for name, filename in model_files.items():
            filepath = self.models_dir / filename
            if filepath.exists():
                try:
                    self.models[name] = joblib.load(filepath)
                    print(f"Loaded {name} model")
                except Exception as e:
                    print(f"Warning: Failed to load {name}: {e}")
    
    def forecast_volume(self, horizon: int = 4, model: str = 'ensemble',
                       include_intervals: bool = True) -> Dict:
        """
        Forecast listing volume.
        
        Args:
            horizon: Number of quarters to forecast
            model: Model to use ('sarima', 'prophet', 'lstm', 'ensemble')
            include_intervals: Include confidence intervals
            
        Returns:
            Dictionary with forecast and optionally confidence intervals
        """
        if model not in self.models:
            # Fallback to simple projection if model not loaded
            return self._simple_projection(horizon)
        
        model_obj = self.models[model]
        
        # Mock historical data (in production, load from database)
        historical_data = pd.Series([40438, 42451, 44464, 44594])
        
        try:
            if include_intervals and hasattr(model_obj, 'predict_with_intervals'):
                if model == 'lstm':
                    result = model_obj.predict_with_intervals(historical_data, steps=horizon)
                else:
                    result = model_obj.predict_with_intervals(steps=horizon)
                
                return {
                    'forecast': result['forecast'].tolist(),
                    'ci_lower': result['ci_lower'].tolist(),
                    'ci_upper': result['ci_upper'].tolist(),
                }
            else:
                if model == 'lstm':
                    pred = model_obj.predict(historical_data, steps=horizon)
                else:
                    pred = model_obj.predict(steps=horizon)
                
                return {'forecast': pred.tolist()}
                
        except Exception as e:
            print(f"Prediction error: {e}")
            return self._simple_projection(horizon)
    
    def forecast_price(self, room_type: str, neighborhood: str,
                      bedrooms: int, bathrooms: Optional[float],
                      accommodates: Optional[int], amenities: List[str],
                      horizon: int = 12) -> Dict:
        """
        Forecast price for a property.
        
        Returns:
            Dictionary with price forecast and recommendations
        """
        # Mock implementation (in production, use XGBoost model)
        base_price = 150  # Base price
        
        # Adjustments based on features
        if room_type == "Entire home/apt":
            base_price *= 1.5
        elif room_type == "Private room":
            base_price *= 0.7
        
        base_price += bedrooms * 30
        base_price += len(amenities) * 5
        
        # Seasonal adjustments
        seasonal_factors = [1.0, 0.95, 1.05, 1.1, 1.15, 1.2,
                           1.25, 1.20, 1.10, 1.05, 1.0, 0.95]
        
        forecast = [base_price * seasonal_factors[i % 12] for i in range(horizon)]
        
        return {
            'forecast': forecast,
            'ci_lower': [p * 0.9 for p in forecast],
            'ci_upper': [p * 1.1 for p in forecast],
            'current_avg': base_price,
            'recommended_price': base_price * 1.05,
            'trend': 'increasing' if seasonal_factors[-1] > seasonal_factors[0] else 'stable',
            'seasonality_factor': max(seasonal_factors) / min(seasonal_factors)
        }
    
    def forecast_occupancy(self, room_type: str, neighborhood: str,
                          bedrooms: int, bathrooms: Optional[float],
                          accommodates: Optional[int], amenities: List[str],
                          price: float, horizon: int = 6) -> Dict:
        """
        Forecast occupancy rate and revenue.
        
        Returns:
            Dictionary with occupancy forecast and revenue estimates
        """
        # Mock implementation (in production, use XGBoost model)
        base_occupancy = 0.70  # 70% occupancy
        
        # Price sensitivity
        market_avg_price = 150
        price_ratio = price / market_avg_price
        occupancy_adjustment = 1.0 - (price_ratio - 1.0) * 0.2  # -20% per 100% price increase
        
        base_occupancy *= max(0.3, min(1.0, occupancy_adjustment))
        
        # Seasonal pattern
        seasonal_pattern = [0.95, 1.0, 1.05, 1.1, 1.15, 1.1]
        
        forecast = []
        for i in range(horizon):
            month = pd.Timestamp('2024-01-01') + pd.DateOffset(months=i)
            occupancy = base_occupancy * seasonal_pattern[i % len(seasonal_pattern)]
            forecast.append({
                'month': month.strftime('%Y-%m'),
                'occupancy_rate': round(occupancy, 3)
            })
        
        avg_occupancy = np.mean([f['occupancy_rate'] for f in forecast])
        days_per_month = 30
        bookings_per_month = days_per_month * avg_occupancy
        revenue_estimate = bookings_per_month * price
        
        return {
            'forecast': forecast,
            'bookings_per_month': bookings_per_month,
            'revenue_estimate': revenue_estimate
        }
    
    def _simple_projection(self, horizon: int) -> Dict:
        """Simple growth-based projection as fallback."""
        # Based on historical growth rate (~3% per quarter)
        current = 44594
        growth_rate = 0.03
        
        forecast = [current * ((1 + growth_rate) ** i) for i in range(1, horizon + 1)]
        
        return {
            'forecast': forecast,
            'ci_lower': [f * 0.95 for f in forecast],
            'ci_upper': [f * 1.05 for f in forecast],
        }


# Singleton instance
_forecast_service = None

def get_forecast_service() -> ForecastService:
    """Get or create forecast service singleton."""
    global _forecast_service
    if _forecast_service is None:
        _forecast_service = ForecastService()
    return _forecast_service
