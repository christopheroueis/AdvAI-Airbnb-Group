"""
LSTM Model for Listing Volume Forecasting
Long Short-Term Memory neural network for time series prediction.
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib
from typing import Tuple, Dict, Optional
import warnings
warnings.filterwarnings('ignore')


class LSTMVolumeModel:
    """LSTM model for forecasting listing volume."""
    
    def __init__(self, lookback: int = 3, units: int = 64):
        """
        Initialize LSTM model.
        
        Args:
            lookback: Number of past quarters to use for prediction
            units: Number of LSTM units in each layer
        """
        self.lookback = lookback
        self.units = units
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.is_fitted = False
        
    def create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training."""
        X, y = [], []
        for i in range(len(data) - self.lookback):
            X.append(data[i:i + self.lookback])
            y.append(data[i + self.lookback])
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape: Tuple) -> None:
        """Build LSTM architecture."""
        self.model = Sequential([
            LSTM(self.units, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(self.units // 2, return_sequences=False),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dense(1)
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
    def fit(self, y_train: pd.Series, epochs: int = 100, 
            validation_split: float = 0.2, verbose: int = 0) -> Dict:
        """
        Train the LSTM model.
        
        Args:
            y_train: Training data
            epochs: Maximum training epochs
            validation_split: Fraction of data for validation
            verbose: Verbosity mode
            
        Returns:
            Training history
        """
        print(f"Training LSTM model (lookback={self.lookback}, units={self.units})...")
        
        # Scale data
        data_scaled = self.scaler.fit_transform(y_train.values.reshape(-1, 1))
        
        # Create sequences
        X, y = self.create_sequences(data_scaled)
        
        if len(X) < 2:
            raise ValueError(f"Not enough data for lookback={self.lookback}. Need at least {self.lookback + 1} samples.")
        
        # Build model
        self.build_model(input_shape=(X.shape[1], X.shape[2]))
        
        # Callbacks
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=20,
            restore_best_weights=True
        )
        
        # Train
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=1,  # Small batch for small dataset
            validation_split=validation_split,
            callbacks=[early_stop],
            verbose=verbose
        )
        
        self.is_fitted = True
        print(f"Training complete. Final loss: {history.history['loss'][-1]:.4f}")
        
        return history.history
    
    def predict(self, y_train: pd.Series, steps: int = 1) -> np.ndarray:
        """
        Generate forecasts.
        
        Args:
            y_train: Historical data to base predictions on
            steps: Number of quarters to forecast
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        # Scale data
        data_scaled = self.scaler.transform(y_train.values.reshape(-1, 1))
        
        # Start with last 'lookback' values
        current_sequence = data_scaled[-self.lookback:].reshape(1, self.lookback, 1)
        
        predictions = []
        for _ in range(steps):
            # Predict next value
            pred_scaled = self.model.predict(current_sequence, verbose=0)
            predictions.append(pred_scaled[0, 0])
            
            # Update sequence (roll forward)
            current_sequence = np.append(
                current_sequence[:, 1:, :],
                pred_scaled.reshape(1, 1, 1),
                axis=1
            )
        
        # Inverse transform predictions
        predictions = np.array(predictions).reshape(-1, 1)
        predictions = self.scaler.inverse_transform(predictions)
        
        return predictions.flatten()
    
    def predict_with_intervals(self, y_train: pd.Series, steps: int = 1,
                               n_simulations: int = 100) -> Dict:
        """
        Generate forecasts with confidence intervals using Monte Carlo dropout.
        
        Args:
            y_train: Historical data
            steps: Number of quarters to forecast
            n_simulations: Number of MC simulations for uncertainty estimation
        """
        all_predictions = []
        
        for _ in range(n_simulations):
            pred = self.predict(y_train, steps)
            all_predictions.append(pred)
        
        all_predictions = np.array(all_predictions)
        
        return {
            'forecast': np.mean(all_predictions, axis=0),
            'ci_lower': np.percentile(all_predictions, 2.5, axis=0),
            'ci_upper': np.percentile(all_predictions, 97.5, axis=0),
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
        """Save the trained model and scaler."""
        if self.model:
            self.model.save(filepath.replace('.pkl', '_model.h5'))
        joblib.dump({
            'scaler': self.scaler,
            'lookback': self.lookback,
            'units': self.units,
            'is_fitted': self.is_fitted
        }, filepath)
        print(f"Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str):
        """Load a trained model."""
        metadata = joblib.load(filepath)
        instance = cls(lookback=metadata['lookback'], units=metadata['units'])
        instance.scaler = metadata['scaler']
        instance.is_fitted = metadata['is_fitted']
        instance.model = keras.models.load_model(filepath.replace('.pkl', '_model.h5'))
        return instance


if __name__ == "__main__":
    # Example usage
    from app.ml.preprocessing import DataPipeline
    
    # Load data
    pipeline = DataPipeline(data_dir="../../../LA_2022.10-2023.9")
    results = pipeline.run_full_pipeline()
    
    train = results['train_volume']
    test = results['test_volume']
    
    # Train model with different lookback values
    for lookback in [2, 3]:
        print(f"\n{'='*60}")
        print(f"Testing lookback={lookback}")
        print('='*60)
        
        model = LSTMVolumeModel(lookback=lookback, units=64)
        
        try:
            history = model.fit(train['total_listings'], epochs=100, verbose=0)
            
            # Evaluate on test set
            y_pred = model.predict(train['total_listings'], steps=len(test))
            metrics = model.evaluate(test['total_listings'].values, y_pred)
            
            print(f"\nTest Set Performance:")
            print(f"RMSE: {metrics['rmse']:.2f}")
            print(f"MAE: {metrics['mae']:.2f}")
            print(f"MAPE: {metrics['mape']:.2f}%")
            
            # Forecast future with uncertainty
            future_forecast = model.predict_with_intervals(
                pd.concat([train['total_listings'], test['total_listings']]),
                steps=4,
                n_simulations=50
            )
            
            print(f"\nFuture Forecast (next 4 quarters):")
            for i, (pred, lower, upper) in enumerate(zip(
                future_forecast['forecast'],
                future_forecast['ci_lower'],
                future_forecast['ci_upper']
            ), start=1):
                print(f"Q{i}: {pred:.0f} (95% CI: {lower:.0f} - {upper:.0f})")
            
        except ValueError as e:
            print(f"Error: {e}")
            continue
    
    # Save best model
    best_model = LSTMVolumeModel(lookback=3, units=64)
    best_model.fit(train['total_listings'], epochs=100, verbose=0)
    best_model.save('../data/models/lstm_volume.pkl')
