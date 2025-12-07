"""
Ensemble Model combining multiple forecasting approaches.
Weighted average of SARIMA, Prophet, LSTM, and XGBoost predictions.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import joblib
import warnings
warnings.filterwarnings('ignore')


class EnsembleForecaster:
    """Ensemble model combining multiple forecasting methods."""
    
    def __init__(self, models: Optional[Dict] = None, weights: Optional[Dict[str, float]] = None):
        """
        Initialize ensemble forecaster.
        
        Args:
            models: Dictionary of fitted models {name: model_instance}
            weights: Dictionary of model weights {name: weight}. Must sum to 1.0
        """
        self.models = models or {}
        self.weights = weights or {}
        self.performance_metrics = {}
        
    def add_model(self, name: str, model, weight: float = None):
        """Add a model to the ensemble."""
        self.models[name] = model
        if weight is not None:
            self.weights[name] = weight
        
    def set_weights(self, weights: Dict[str, float]):
        """
        Set model weights.
        
        Args:
            weights: Dictionary {model_name: weight}. Must sum to 1.0
        """
        if abs(sum(weights.values()) - 1.0) > 1e-6:
            raise ValueError(f"Weights must sum to 1.0, got {sum(weights.values())}")
        
        # Validate all models exist
        for name in weights:
            if name not in self.models:
                raise ValueError(f"Model '{name}' not found in ensemble")
        
        self.weights = weights
    
    def auto_weight_by_performance(self, metrics: Dict[str, Dict[str, float]], 
                                   metric: str = 'mape'):
        """
        Automatically set weights based on model performance.
        Lower error = higher weight (inverse weighting).
        
        Args:
            metrics: Dictionary {model_name: {metric: value}}
            metric: Metric to use for weighting ('rmse', 'mae', or 'mape')
        """
        # Extract metric values
        scores = {name: metrics[name][metric] for name in metrics}
        
        # Inverse weighting (lower error = higher weight)
        inverse_scores = {name: 1 / score for name, score in scores.items()}
        total_inverse = sum(inverse_scores.values())
        
        # Normalize to sum to 1.0
        self.weights = {name: inv / total_inverse for name, inv in inverse_scores.items()}
        
        print("Auto-weighted ensemble:")
        for name, weight in sorted(self.weights.items(), key=lambda x: x[1], reverse=True):
            print(f"  {name}: {weight:.3f} (based on {metric}={scores[name]:.2f})")
    
    def predict_volume(self, train_data: pd.Series, steps: int = 1) -> np.ndarray:
        """
        Generate ensemble forecast for listing volume.
        
        Args:
            train_data: Historical time series data
            steps: Number of periods to forecast
            
        Returns:
            Ensemble predictions
        """
        if not self.weights:
            raise ValueError("Weights must be set before prediction")
        
        predictions = {}
        
        # Get predictions from each model
        for name, model in self.models.items():
            if name not in self.weights:
                continue
                
            try:
                if hasattr(model, 'predict'):
                    if name == 'lstm':
                        pred = model.predict(train_data, steps=steps)
                    else:
                        pred = model.predict(steps=steps)
                    predictions[name] = pred
            except Exception as e:
                print(f"Warning: {name} prediction failed: {e}")
                continue
        
        # Weighted average
        ensemble_pred = np.zeros(steps)
        total_weight = 0
        
        for name, pred in predictions.items():
            weight = self.weights.get(name, 0)
            ensemble_pred += weight * pred
            total_weight += weight
        
        # Normalize if some models failed
        if total_weight > 0 and abs(total_weight - 1.0) > 1e-6:
            ensemble_pred /= total_weight
        
        return ensemble_pred
    
    def predict_with_intervals(self, train_data: pd.Series, steps: int = 1,
                               alpha: float = 0.05) -> Dict:
        """
        Generate ensemble forecast with confidence intervals.
        Uses weighted average of individual model intervals.
        
        Args:
            train_data: Historical time series data
            steps: Number of periods to forecast
            alpha: Significance level for confidence intervals
            
        Returns:
            Dictionary with forecast, ci_lower, ci_upper
        """
        all_forecasts = []
        all_lowers = []
        all_uppers = []
        
        for name, model in self.models.items():
            if name not in self.weights:
                continue
            
            try:
                if hasattr(model, 'predict_with_intervals'):
                    if name == 'lstm':
                        result = model.predict_with_intervals(train_data, steps=steps)
                    else:
                        result = model.predict_with_intervals(steps=steps, alpha=alpha)
                    
                    weight = self.weights[name]
                    all_forecasts.append(weight * result['forecast'])
                    all_lowers.append(weight * result['ci_lower'])
                    all_uppers.append(weight * result['ci_upper'])
            except Exception as e:
                print(f"Warning: {name} interval prediction failed: {e}")
                continue
        
        if not all_forecasts:
            raise ValueError("No valid interval predictions obtained")
        
        return {
            'forecast': np.sum(all_forecasts, axis=0),
            'ci_lower': np.sum(all_lowers, axis=0),
            'ci_upper': np.sum(all_uppers, axis=0),
        }
    
    def evaluate_models(self, train_data: pd.Series, test_data: pd.Series) -> Dict:
        """
        Evaluate all models on test data.
        
        Args:
            train_data: Training time series
            test_data: Test time series
            
        Returns:
            Dictionary of performance metrics for each model
        """
        from sklearn.metrics import mean_squared_error, mean_absolute_error
        
        metrics = {}
        steps = len(test_data)
        
        for name, model in self.models.items():
            try:
                if name == 'lstm':
                    pred = model.predict(train_data, steps=steps)
                else:
                    pred = model.predict(steps=steps)
                
                y_true = test_data.values if hasattr(test_data, 'values') else test_data
                
                metrics[name] = {
                    'rmse': np.sqrt(mean_squared_error(y_true, pred)),
                    'mae': mean_absolute_error(y_true, pred),
                    'mape': np.mean(np.abs((y_true - pred) / y_true)) * 100,
                }
                
                print(f"\n{name.upper()} Performance:")
                print(f"  RMSE: {metrics[name]['rmse']:.2f}")
                print(f"  MAE: {metrics[name]['mae']:.2f}")
                print(f"  MAPE: {metrics[name]['mape']:.2f}%")
                
            except Exception as e:
                print(f"Warning: {name} evaluation failed: {e}")
                continue
        
        self.performance_metrics = metrics
        return metrics
    
    def save(self, filepath: str):
        """Save ensemble configuration."""
        joblib.dump({
            'weights': self.weights,
            'performance_metrics': self.performance_metrics,
        }, filepath)
        print(f"Ensemble configuration saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str, models: Dict):
        """Load ensemble configuration with provided models."""
        data = joblib.load(filepath)
        instance = cls(models=models, weights=data['weights'])
        instance.performance_metrics = data['performance_metrics']
        return instance


if __name__ == "__main__":
    # Example usage
    from app.ml.preprocessing import DataPipeline
    from app.ml.models.sarima import SARIMAVolumeModel
    from app.ml.models.prophet_model import ProphetVolumeModel
    from app.ml.models.lstm_model import LSTMVolumeModel
    
    # Load data
    pipeline = DataPipeline(data_dir="../../../LA_2022.10-2023.9")
    results = pipeline.run_full_pipeline()
    
    train = results['train_volume']
    test = results['test_volume']
    
    print("="*60)
    print("Building Ensemble Forecaster")
    print("="*60)
    
    # Train individual models
    print("\nTraining individual models...")
    
    sarima = SARIMAVolumeModel(order=(1, 1, 1), seasonal_order=(1, 0, 1, 4))
    sarima.fit(train['total_listings'])
    
    prophet = ProphetVolumeModel()
    prophet.fit(train)
    
    lstm = LSTMVolumeModel(lookback=3, units=64)
    lstm.fit(train['total_listings'], epochs=100, verbose=0)
    
    # Create ensemble
    ensemble = EnsembleForecaster()
    ensemble.add_model('sarima', sarima)
    ensemble.add_model('prophet', prophet)
    ensemble.add_model('lstm', lstm)
    
    # Evaluate all models
    print("\n" + "="*60)
    print("Evaluating Models")
    print("="*60)
    
    metrics = ensemble.evaluate_models(train['total_listings'], test['total_listings'])
    
    # Auto-weight by performance
    print("\n" + "="*60)
    print("Auto-weighting Ensemble")
    print("="*60)
    
    ensemble.auto_weight_by_performance(metrics, metric='mape')
    
    # Ensemble prediction
    print("\n" + "="*60)
    print("Ensemble Forecast")
    print("="*60)
    
    ensemble_pred = ensemble.predict_volume(train['total_listings'], steps=len(test))
    
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    rmse = np.sqrt(mean_squared_error(test['total_listings'].values, ensemble_pred))
    mae = mean_absolute_error(test['total_listings'].values, ensemble_pred)
    mape = np.mean(np.abs((test['total_listings'].values - ensemble_pred) / test['total_listings'].values)) * 100
    
    print(f"\nEnsemble Test Performance:")
    print(f"RMSE: {rmse:.2f}")
    print(f"MAE: {mae:.2f}")
    print(f"MAPE: {mape:.2f}%")
    
    # Future forecast with intervals
    full_train = pd.concat([train['total_listings'], test['total_listings']])
    future = ensemble.predict_with_intervals(full_train, steps=4)
    
    print(f"\nFuture Forecast (next 4 quarters):")
    for i, (pred, lower, upper) in enumerate(zip(
        future['forecast'],
        future['ci_lower'],
        future['ci_upper']
    ), start=1):
        print(f"2024 Q{i}: {pred:.0f} (95% CI: {lower:.0f} - {upper:.0f})")
    
    # Save ensemble
    ensemble.save('../data/models/ensemble_volume.pkl')
