"""
Prophet Model for Listing Volume Forecasting
Meta's Prophet for robust seasonal forecasting with trend changepoints.
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib
from typing import Dict
import warnings
warnings.filterwarnings('ignore')


class ProphetVolumeModel:
    """Prophet model for forecasting listing volume."""
    
    def __init__(self, seasonality_mode: str = 'multiplicative',
                 changepoint_prior_scale: float = 0.05):
        """
        Initialize Prophet model.
        
        Args:
            seasonality_mode: 'additive' or 'multiplicative'
            changepoint_prior_scale: Flexibility of trend (higher = more flexible)
        """
        self.model = Prophet(
            seasonality_mode=seasonality_mode,
            changepoint_prior_scale=changepoint_prior_scale,
            yearly_seasonality=False,  # We have quarterly data
            weekly_seasonality=False,
            daily_seasonality=False,
        )
        
        # Add quarterly seasonality
        self.model.add_seasonality(
            name='quarterly',
            period=365.25/4,  # ~91.3 days
            fourier_order=5
        )
        
        self.seasonality_mode = seasonality_mode
        self.is_fitted = False
        
    def fit(self, df: pd.DataFrame) -> None:
        """
        Train the Prophet model.
        
        Args:
            df: DataFrame with 'quarter' and 'total_listings' columns
        """
        print("Training Prophet model...")
        
        # Convert to Prophet format (ds, y)
        prophet_df = pd.DataFrame({
            'ds': pd.to_datetime(df['quarter'].str.replace('Q', '-Q'), format='%Y-Q%q'),
            'y': df['total_listings']
        })
        
        self.model.fit(prophet_df)
        self.is_fitted = True
        print("Model trained successfully")
        
    def predict(self, periods: int = 1) -> np.ndarray:
        """
        Generate forecasts.
        
        Args:
            periods: Number of quarters to forecast
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        # Create future dataframe
        future = self.model.make_future_dataframe(
            periods=periods,
            freq='Q',  # Quarterly
            include_history=False
        )
        
        forecast = self.model.predict(future)
        return forecast['yhat'].values
    
    def predict_with_intervals(self, periods: int = 1) -> Dict:
        """Generate forecasts with confidence intervals."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        future = self.model.make_future_dataframe(
            periods=periods,
            freq='Q',
            include_history=False
        )
        
        forecast = self.model.predict(future)
        
        return {
            'forecast': forecast['yhat'].values,
            'ci_lower': forecast['yhat_lower'].values,
            'ci_upper': forecast['yhat_upper'].values,
            'dates': forecast['ds'].values,
        }
    
    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate evaluation metrics."""
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        return {
            'rmse': rmse,
            'mae': mae,
            'mape': mape,
        }
    
    def save(self, filepath: str) -> None:
        """Save the trained model."""
        joblib.dump(self, filepath)
        print(f"Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str):
        """Load a trained model."""
        return joblib.load(filepath)
    
    def plot_components(self, periods: int = 4):
        """Plot forecast components (trend, seasonality)."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before plotting")
        
        future = self.model.make_future_dataframe(periods=periods, freq='Q')
        forecast = self.model.predict(future)
        
        from prophet.plot import plot_components_plotly
        fig = plot_components_plotly(self.model, forecast)
        return fig


if __name__ == "__main__":
    # Example usage
    from app.ml.preprocessing import DataPipeline
    
    # Load data
    pipeline = DataPipeline(data_dir="../../../LA_2022.10-2023.9")
    results = pipeline.run_full_pipeline()
    
    train = results['train_volume']
    test = results['test_volume']
    
    # Train model
    model = ProphetVolumeModel(
        seasonality_mode='additive',
        changepoint_prior_scale=0.05
    )
    model.fit(train)
    
    # Evaluate on test set
    y_pred = model.predict(periods=len(test))
    metrics = model.evaluate(test['total_listings'].values, y_pred)
    
    print("\nTest Set Performance:")
    print(f"RMSE: {metrics['rmse']:.2f}")
    print(f"MAE: {metrics['mae']:.2f}")
    print(f"MAPE: {metrics['mape']:.2f}%")
    
    # Forecast future
    future_forecast = model.predict_with_intervals(periods=4)
    print("\nFuture Forecast (next 4 quarters):")
    for i, (pred, lower, upper) in enumerate(zip(
        future_forecast['forecast'],
        future_forecast['ci_lower'],
        future_forecast['ci_upper']
    ), start=1):
        print(f"Q{i}: {pred:.0f} (95% CI: {lower:.0f} - {upper:.0f})")
    
    # Save model
    model.save('../data/models/prophet_volume.pkl')
