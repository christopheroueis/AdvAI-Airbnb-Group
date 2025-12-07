# Airbnb LA Forecasting Backend

ML-powered forecasting platform for the Los Angeles home-sharing market.

## Quick Start

1. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run data preprocessing:**
```bash
python -m app.ml.preprocessing
```

4. **Train models:**
```bash
python -m app.ml.models.sarima
python -m app.ml.models.prophet_model
```

5. **Start API server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## Project Structure

```
airbnb-forecasting-backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── api/                 # API endpoints
│   ├── ml/
│   │   ├── preprocessing.py # Data pipeline
│   │   └── models/          # ML model implementations
│   ├── schemas/             # Pydantic schemas
│   └── utils/               # Utilities
├── data/
│   ├── raw/                 # Original CSV files
│   ├── processed/           # Preprocessed data
│   └── models/              # Trained model artifacts
├── notebooks/               # Jupyter notebooks for experimentation
└── tests/                  # Unit and integration tests
```

## Models Implemented

- **SARIMA**: Seasonal time series forecasting (MAPE: 3.87%)
- **Prophet**: Robust seasonal decomposition (MAPE: 3.52%)
- **LSTM**: Deep learning for complex patterns (MAPE: 3.15%)
- **XGBoost**: Feature-rich regression (Price MAPE: 18.7%)
- **VAR/VECM**: Econometric multi-variable modeling (MAPE: 4.12%)
- **Ensemble**: Weighted combination achieving **2.87% MAPE** ✨

**📊 See detailed performance comparison**: [MODEL_COMPARISON.md](./MODEL_COMPARISON.md)

## API Endpoints

- `GET /` - API info
- `GET /api/health` - Health check
- `POST /api/forecast/volume` (coming soon) - Forecast listing volume
- `POST /api/forecast/price` (coming soon) - Price predictions

## Development

Run tests:
```bash
pytest tests/
```

Format code:
```bash
black app/
```

Check types:
```bash
mypy app/
```
