# Example: Testing Scenario Simulation

## Setup
First, start the API server:
```bash
cd airbnb-forecasting-backend
uvicorn app.main:app --reload
```

## Get Available Scenarios
```bash
curl http://localhost:8000/api/scenarios/scenarios
```

Response:
```json
[
  {
    "id": "optimistic",
    "name": "Optimistic Growth",
    "description": "Major events drive tourism, no major disruptions"
  },
  {
    "id": "pessimistic",
    "name": "Pessimistic (Multiple Disruptions)",
    "description": "Economic downturn + wildfires + extreme weather"
  },
  ...
]
```

## Get Available Events
```bash
curl http://localhost:8000/api/scenarios/events
```

Response:
```json
[
  {
    "event_type": "covid_19",
    "name": "COVID-19 Pandemic",
    "description": "Impact of COVID-19 on travel",
    "impact_multiplier": -0.6
  },
  {
    "event_type": "wildfire",
    "name": "LA Wildfires",
    "description": "Major wildfire events",
    "impact_multiplier": -0.3
  },
  ...
]
```

## Simulate Predefined Scenario
```bash
curl -X POST http://localhost:8000/api/scenarios/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "pessimistic",
    "horizon": 4,
    "base_model": "ensemble"
  }'
```

## Simulate Custom Scenario
```bash
curl -X POST http://localhost:8000/api/scenarios/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "My Custom Scenario",
    "events": ["wildfire", "extreme_weather"],
    "custom_shocks": [
      {"period": "2024-Q3", "impact": -0.25}
    ],
    "horizon": 4
  }'
```

Response:
```json
{
  "scenario_name": "My Custom Scenario",
  "base_forecast": [46200, 47500, 48800, 50100],
  "adjusted_forecast": [46200, 47500, 36600, 50100],
  "total_impact_pct": [0, 0, -25, 0],
  "summary": {
    "avg_impact_pct": -6.25,
    "max_negative_impact_pct": -25,
    "max_positive_impact_pct": 0,
    "events_included": ["wildfire", "extreme_weather"]
  },
  "periods": ["2024Q1", "2024Q2", "2024Q3", "2024Q4"]
}
```

## Compare Multiple Scenarios
```bash
curl -X POST http://localhost:8000/api/scenarios/compare \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_ids": ["optimistic", "baseline", "pessimistic"],
    "horizon": 4
  }'
```

This returns an array of scenario results for side-by-side comparison.

## Model Training with Logging

The logging system automatically tracks all model training:

```python
from app.utils.logger import get_model_logger
from app.ml.models.sarima import SARIMAVolumeModel

logger = get_model_logger()

# Train model
model = SARIMAVolumeModel()
logger.log_training_start("SARIMA", {"order": (1,1,1), "seasonal_order": (1,0,1,4)})

# ... training code ...

# Log results
logger.log_evaluation_results(
    model_name="SARIMA",
    model_version="v1.0",
    task="volume",
    metrics={"rmse": 920, "mae": 780, "mape": 3.8},
    train_samples=3,
    test_samples=1,
    training_time=5.2,
    hyperparameters={"order": (1,1,1)},
    exogenous_vars=["covid_19", "wildfire"],
    notes="Baseline model"
)

# Compare all models
logger.compare_models(task="volume", metric="mape")

# Get best model
best = logger.get_best_model(task="volume")
```

## View Logs

All logs are saved to `data/logs/`:
- `training_YYYYMMDD.log` - Detailed training logs
- `model_metrics.csv` - All model metrics in CSV format
- `model_report_*.html` - HTML comparison reports
