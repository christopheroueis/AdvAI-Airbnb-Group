"""
XGBoost Model for Price and Occupancy Forecasting
Gradient boosting model for feature-rich prediction tasks.
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib
from typing import Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class XGBoostForecastModel:
    """XGBoost model for forecasting with rich features."""
    
    def __init__(self, task: str = 'volume', **xgb_params):
        """
        Initialize XGBoost model.
        
        Args:
            task: 'volume', 'price', or 'occupancy'
            **xgb_params: XGBoost hyperparameters
        """
        self.task = task
        
        # Default parameters
        default_params = {
            'objective': 'reg:squarederror',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
        }
        default_params.update(xgb_params)
        
        self.model = xgb.XGBRegressor(**default_params)
        self.feature_names = None
        self.is_fitted = False
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features for XGBoost.
        
        Args:
            df: DataFrame with property features
            
        Returns:
            X, y tuple
        """
        # Feature columns
        feature_cols = [
            'bedrooms', 'beds', 'accommodates',
            'amenities_count', 'has_wifi', 'has_kitchen', 'has_parking',
            'quarter_num', 'is_summer',
            'neighborhood_density', 'is_superhost', 'multi_listing_host'
        ]
        
        # Add review features if available
        if 'review_scores_rating' in df.columns:
            feature_cols.append('review_scores_rating')
        if 'number_of_reviews' in df.columns:
            feature_cols.append('number_of_reviews')
        
        # Select available features
        available_features = [col for col in feature_cols if col in df.columns]
        
        X = df[available_features].copy()
        
        # Target variable based on task
        if self.task == 'price':
            y = df['price']
        elif self.task == 'occupancy':
            y = 1 - (df['availability_365'] / 365)  # Occupancy rate
        else:  # volume (aggregate task)
            y = df.groupby('source')['id'].transform('count')
        
        # Fill missing values
        X = X.fillna(X.median())
        
        self.feature_names = X.columns.tolist()
        
        return X, y
    
    def fit(self, df: pd.DataFrame, verbose: bool = True) -> None:
        """Train the XGBoost model."""
        if verbose:
            print(f"Training XGBoost model for {self.task}...")
        
        X, y = self.prepare_features(df)
        
        self.model.fit(
            X, y,
            eval_set=[(X, y)],
            verbose=False
        )
        
        self.is_fitted = True
        
        if verbose:
            print(f"Model trained on {len(X)} samples with {len(self.feature_names)} features")
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Generate predictions."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        X, _ = self.prepare_features(df)
        predictions = self.model.predict(X)
        
        return predictions
    
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
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance scores."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    def hyperparameter_tuning(self, df: pd.DataFrame, 
                             param_grid: Optional[Dict] = None) -> Dict:
        """
        Perform grid search for hyperparameter tuning.
        
        Args:
            df: Training data
            param_grid: Dictionary of parameters to search
            
        Returns:
            Best parameters found
        """
        if param_grid is None:
            param_grid = {
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.3],
                'n_estimators': [50, 100, 200],
                'subsample': [0.7, 0.8, 0.9],
            }
        
        X, y = self.prepare_features(df)
        
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=3)
        
        grid_search = GridSearchCV(
            self.model,
            param_grid,
            cv=tscv,
            scoring='neg_mean_squared_error',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X, y)
        
        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best RMSE: {np.sqrt(-grid_search.best_score_):.2f}")
        
        # Update model with best parameters
        self.model = grid_search.best_estimator_
        self.is_fitted = True
        
        return grid_search.best_params_
    
    def save(self, filepath: str) -> None:
        """Save the trained model."""
        joblib.dump({
            'model': self.model,
            'task': self.task,
            'feature_names': self.feature_names,
            'is_fitted': self.is_fitted
        }, filepath)
        print(f"Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str):
        """Load a trained model."""
        data = joblib.load(filepath)
        instance = cls(task=data['task'])
        instance.model = data['model']
        instance.feature_names = data['feature_names']
        instance.is_fitted = data['is_fitted']
        return instance


if __name__ == "__main__":
    # Example usage
    from app.ml.preprocessing import DataPipeline
    
    # Load data
    pipeline = DataPipeline(data_dir="../../../LA_2022.10-2023.9")
    results = pipeline.run_full_pipeline()
    
    listings_ml = results['listings_ml']
    
    # Filter out extreme prices for training
    listings_ml_clean = listings_ml[
        (listings_ml['price'] > 0) & 
        (listings_ml['price'] < listings_ml['price'].quantile(0.99))
    ].copy()
    
    # Train price prediction model
    print("="*60)
    print("Training Price Prediction Model")
    print("="*60)
    
    price_model = XGBoostForecastModel(task='price')
    
    # Split by quarter for train/test
    train_data = listings_ml_clean[listings_ml_clean['source'].isin(['2022Q4', '2023Q1', '2023Q2'])]
    test_data = listings_ml_clean[listings_ml_clean['source'] == '2023Q3']
    
    # Train
    price_model.fit(train_data)
    
    # Evaluate
    y_pred = price_model.predict(test_data)
    X_test, y_test = price_model.prepare_features(test_data)
    metrics = price_model.evaluate(y_test.values, y_pred)
    
    print(f"\nTest Set Performance (Price Prediction):")
    print(f"RMSE: ${metrics['rmse']:.2f}")
    print(f"MAE: ${metrics['mae']:.2f}")
    print(f"MAPE: {metrics['mape']:.2f}%")
    
    # Feature importance
    print(f"\nTop 10 Most Important Features:")
    importance = price_model.get_feature_importance()
    print(importance.head(10))
    
    # Save model
    price_model.save('../data/models/xgboost_price.pkl')
    
    # Train occupancy prediction model
    print("\n" + "="*60)
    print("Training Occupancy Prediction Model")
    print("="*60)
    
    occupancy_model = XGBoostForecastModel(task='occupancy')
    occupancy_model.fit(train_data)
    
    y_pred_occ = occupancy_model.predict(test_data)
    X_test_occ, y_test_occ = occupancy_model.prepare_features(test_data)
    metrics_occ = occupancy_model.evaluate(y_test_occ.values, y_pred_occ)
    
    print(f"\nTest Set Performance (Occupancy Prediction):")
    print(f"RMSE: {metrics_occ['rmse']:.4f}")
    print(f"MAE: {metrics_occ['mae']:.4f}")
    print(f"MAPE: {metrics_occ['mape']:.2f}%")
    
    occupancy_model.save('../data/models/xgboost_occupancy.pkl')
