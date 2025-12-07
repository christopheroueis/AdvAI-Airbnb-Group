"""
Logging utility for model training and evaluation results.
Tracks model performance metrics and saves to structured log files.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd


class ModelLogger:
    """Logger for ML model training and evaluation."""
    
    def __init__(self, log_dir: str = "data/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up file logging
        self.setup_file_logger()
        
        # Initialize metrics dataframe
        self.metrics_file = self.log_dir / "model_metrics.csv"
        self.load_or_create_metrics_log()
        
    def setup_file_logger(self):
        """Set up file-based logging."""
        log_file = self.log_dir / f"training_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('ModelTraining')
        
    def load_or_create_metrics_log(self):
        """Load existing metrics or create new log."""
        if self.metrics_file.exists():
            self.metrics_df = pd.read_csv(self.metrics_file)
        else:
            self.metrics_df = pd.DataFrame(columns=[
                'timestamp', 'model_name', 'model_version', 'task',
                'rmse', 'mae', 'mape', 'r2',
                'train_samples', 'test_samples', 'training_time_sec',
                'hyperparameters', 'exogenous_vars', 'notes'
            ])
    
    def log_training_start(self, model_name: str, config: Dict[str, Any]):
        """Log the start of model training."""
        self.logger.info(f"="*60)
        self.logger.info(f"Starting training: {model_name}")
        self.logger.info(f"Configuration: {json.dumps(config, indent=2)}")
        self.logger.info(f"="*60)
    
    def log_training_progress(self, epoch: int, loss: float, val_loss: Optional[float] = None):
        """Log training progress (for neural networks)."""
        msg = f"Epoch {epoch}: loss={loss:.4f}"
        if val_loss is not None:
            msg += f", val_loss={val_loss:.4f}"
        self.logger.info(msg)
    
    def log_evaluation_results(self, model_name: str, model_version: str,
                               task: str, metrics: Dict[str, float],
                               train_samples: int, test_samples: int,
                               training_time: float,
                               hyperparameters: Dict[str, Any],
                               exogenous_vars: Optional[list] = None,
                               notes: str = ""):
        """
        Log model evaluation results and save to metrics file.
        
        Args:
            model_name: Name of the model (e.g., 'SARIMA', 'LSTM')
            model_version: Version string (e.g., 'v1.0')
            task: Forecasting task (e.g., 'volume', 'price')
            metrics: Dictionary of evaluation metrics
            train_samples: Number of training samples
            test_samples: Number of test samples
            training_time: Training time in seconds
            hyperparameters: Model hyperparameters
            exogenous_vars: List of exogenous variables used
            notes: Additional notes
        """
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Evaluation Results: {model_name} ({model_version})")
        self.logger.info(f"Task: {task}")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Metrics:")
        for metric, value in metrics.items():
            self.logger.info(f"  {metric.upper()}: {value:.4f}")
        self.logger.info(f"Training samples: {train_samples}")
        self.logger.info(f"Test samples: {test_samples}")
        self.logger.info(f"Training time: {training_time:.2f}s")
        if exogenous_vars:
            self.logger.info(f"Exogenous variables: {', '.join(exogenous_vars)}")
        self.logger.info(f"{'='*60}\n")
        
        # Add to metrics dataframe
        new_row = {
            'timestamp': datetime.now().isoformat(),
            'model_name': model_name,
            'model_version': model_version,
            'task': task,
            'rmse': metrics.get('rmse', None),
            'mae': metrics.get('mae', None),
            'mape': metrics.get('mape', None),
            'r2': metrics.get('r2', None),
            'train_samples': train_samples,
            'test_samples': test_samples,
            'training_time_sec': training_time,
            'hyperparameters': json.dumps(hyperparameters),
            'exogenous_vars': json.dumps(exogenous_vars) if exogenous_vars else None,
            'notes': notes
        }
        
        self.metrics_df = pd.concat([
            self.metrics_df,
            pd.DataFrame([new_row])
        ], ignore_index=True)
        
        # Save to CSV
        self.metrics_df.to_csv(self.metrics_file, index=False)
    
    def compare_models(self, task: str = None, metric: str = 'mape') -> pd.DataFrame:
        """
        Compare model performance.
        
        Args:
            task: Filter by task (e.g., 'volume', 'price')
            metric: Metric to sort by (default: 'mape')
            
        Returns:
            DataFrame with model comparison
        """
        df = self.metrics_df.copy()
        
        if task:
            df = df[df['task'] == task]
        
        if df.empty:
            self.logger.warning(f"No metrics found for task: {task}")
            return df
        
        # Get latest version of each model
        df = df.sort_values('timestamp', ascending=False)
        df = df.drop_duplicates(subset=['model_name', 'task'], keep='first')
        
        # Sort by metric (ascending = better for error metrics)
        if metric in df.columns:
            df = df.sort_values(metric, ascending=True)
        
        self.logger.info(f"\nModel Comparison (Task: {task or 'all'}, Sorted by {metric}):")
        self.logger.info("\n" + df[['model_name', 'rmse', 'mae', 'mape', 'training_time_sec']].to_string())
        
        return df
    
    def get_best_model(self, task: str, metric: str = 'mape') -> Dict[str, Any]:
        """Get the best performing model for a task."""
        comparison = self.compare_models(task=task, metric=metric)
        
        if comparison.empty:
            return None
        
        best = comparison.iloc[0]
        
        result = {
            'model_name': best['model_name'],
            'model_version': best['model_version'],
            'metrics': {
                'rmse': best['rmse'],
                'mae': best['mae'],
                'mape': best['mape'],
            },
            'timestamp': best['timestamp']
        }
        
        self.logger.info(f"\nBest model for {task}: {result['model_name']} (MAPE: {result['metrics']['mape']:.2f}%)")
        
        return result
    
    def export_report(self, output_file: str = None):
        """Export comprehensive model comparison report."""
        if output_file is None:
            output_file = self.log_dir / f"model_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Create HTML report
        html = "<html><head><title>Model Performance Report</title>"
        html += "<style>table {border-collapse: collapse;} th, td {border: 1px solid black; padding: 8px;}</style>"
        html += "</head><body>"
        html += f"<h1>Model Performance Report</h1>"
        html += f"<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
        
        # Overall comparison
        html += "<h2>Overall Model Comparison</h2>"
        html += self.metrics_df.to_html(index=False)
        
        # Best models by task
        html += "<h2>Best Models by Task</h2>"
        for task in self.metrics_df['task'].unique():
            best = self.get_best_model(task, metric='mape')
            if best:
                html += f"<h3>{task.capitalize()}</h3>"
                html += f"<p><strong>{best['model_name']}</strong> - MAPE: {best['metrics']['mape']:.2f}%</p>"
        
        html += "</body></html>"
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        self.logger.info(f"Report exported to: {output_file}")
        return output_file


# Singleton instance
_model_logger = None

def get_model_logger() -> ModelLogger:
    """Get or create model logger singleton."""
    global _model_logger
    if _model_logger is None:
        _model_logger = ModelLogger()
    return _model_logger
