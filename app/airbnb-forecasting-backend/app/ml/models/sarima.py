"""
SARIMA Model for Listing Volume Forecasting
Seasonal AutoRegressive Integrated Moving Average model for quarterly predictions.
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib
from typing import Tuple, Dict
import warnings
warnings.filterwarnings('ignore')


class SARIMAVolumeModel:
    """SARIMA model for forecasting listing volume."""
    
    def __init__(self, order: Tuple[int, int, int] = (1, 1, 1),
                 seasonal_order: Tuple[int, int, int, int] = (1, 0, 1, 4)):
        """
        Initialize SARIMA model.
        
        Args:
            order: (p, d, q) for AR, I, MA
            seasonal_order: (P, D, Q, s) for seasonal components (s=4 for quarterly)
        """
        self.order = order
        self.seasonal_order = seasonal_order
        self.model = None
        self.model_fit = None
        
    def fit(self, y_train: pd.Series) -> None:
        """Train the SARIMA model."""
        print(f"Training SARIMA{self.order}x{self.seasonal_order} model...")
        
        self.model = SARIMAX(
            y_train,
            order=self.order,
            seasonal_order=self.seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        
        self.model_fit = self.model.fit(disp=False)
        print(f"Model trained. AIC: {self.model_fit.aic:.2f}")
        
    def predict(self, steps: int = 1) -> np.ndarray:
        """Generate forecasts."""
        if self.model_fit is None:
            raise ValueError("Model must be fitted before making predictions")
        
        forecast = self.model_fit.forecast(steps=steps)
        return forecast.values
    
    def predict_with_intervals(self, steps: int = 1, alpha: float = 0.05) -> Dict:
        """Generate forecasts with confidence intervals."""
        if self.model_fit is None:
            raise ValueError("Model must be fitted before making predictions")
        
        forecast_result = self.model_fit.get_forecast(steps=steps)
        forecast_df = forecast_result.summary_frame(alpha=alpha)
        
        return {
            'forecast': forecast_df['mean'].values,
            'ci_lower': forecast_df['mean_ci_lower'].values,
            'ci_upper': forecast_df['mean_ci_upper'].values,
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


def grid_search_sarima(y_train: pd.Series, 
                       p_values: range, d_values: range, q_values: range,
                       P_values: range, D_values: range, Q_values: range,
                       s: int = 4) -> Tuple[Tuple, Tuple, float]:
    """
    Grid search for optimal SARIMA parameters.
    
    Returns:
        Best (p,d,q), (P,D,Q,s), and AIC score.
    """
    best_aic = np.inf
    best_order = None
    best_seasonal = None
    
    total_combinations = len(p_values) * len(d_values) * len(q_values) * \
                        len(P_values) * len(D_values) * len(Q_values)
    
    print(f"Testing {total_combinations} combinations...")
    tested = 0
    
    for p in p_values:
        for d in d_values:
            for q in q_values:
                for P in P_values:
                    for D in D_values:
                        for Q in Q_values:
                            try:
                                model = SARIMAX(
                                    y_train,
                                    order=(p, d, q),
                                    seasonal_order=(P, D, Q, s),
                                    enforce_stationarity=False,
                                    enforce_invertibility=False
                                )
                                result = model.fit(disp=False)
                                
                                tested += 1
                                if result.aic < best_aic:
                                    best_aic = result.aic
                                    best_order = (p, d, q)
                                    best_seasonal = (P, D, Q, s)
                                    print(f"  New best: SARIMA{best_order}x{best_seasonal}, AIC={best_aic:.2f}")
                            except:
                                continue
    
    print(f"\nTested {tested}/{total_combinations} combinations")
    print(f"Best model: SARIMA{best_order}x{best_seasonal}")
    print(f"Best AIC: {best_aic:.2f}")
    
    return best_order, best_seasonal, best_aic


if __name__ == "__main__":
    # Example usage
    from app.ml.preprocessing import DataPipeline
    
    # Load data
    pipeline = DataPipeline(data_dir="../../../LA_2022.10-2023.9")
    results = pipeline.run_full_pipeline()
    
    train = results['train_volume']
    test = results['test_volume']
    
    # Grid search for best parameters (optional, time-consuming)
    # best_order, best_seasonal, _ = grid_search_sarima(
    #     train['total_listings'],
    #     p_values=range(0, 3), d_values=[0, 1], q_values=range(0, 3),
    #     P_values=range(0, 2), D_values=[0, 1], Q_values=range(0, 2),
    #     s=4
    # )
    
    # Or use predetermined parameters
    best_order = (1, 1, 1)
    best_seasonal = (1, 0, 1, 4)
    
    # Train model
    model = SARIMAVolumeModel(order=best_order, seasonal_order=best_seasonal)
    model.fit(train['total_listings'])
    
    # Evaluate on test set
    y_pred = model.predict(steps=len(test))
    metrics = model.evaluate(test['total_listings'].values, y_pred)
    
    print("\nTest Set Performance:")
    print(f"RMSE: {metrics['rmse']:.2f}")
    print(f"MAE: {metrics['mae']:.2f}")
    print(f"MAPE: {metrics['mape']:.2f}%")
    
    # Forecast future
    future_forecast = model.predict_with_intervals(steps=4)
    print("\nFuture Forecast (next 4 quarters):")
    for i, (pred, lower, upper) in enumerate(zip(
        future_forecast['forecast'],
        future_forecast['ci_lower'],
        future_forecast['ci_upper']
    ), start=1):
        print(f"Q{i}: {pred:.0f} (95% CI: {lower:.0f} - {upper:.0f})")
    
    # Save model
    model.save('../data/models/sarima_volume.pkl')
