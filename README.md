# Airbnb Forecasting Project

This repository contains a comprehensive Airbnb forecasting tool with machine learning models for predicting listing volumes, prices, and occupancy rates.

## Repository Structure

```
├── app/                          # Main application directory
│   ├── airbnb-forecasting-backend/   # Backend API and ML models
│   ├── airbnb-forecasting-frontend/  # React frontend application
│   ├── LA_2022.10-2023.9/           # Training data
│   ├── QUICKSTART.md               # Quick start guide
│   ├── PRESENTATION_GUIDE.md       # Presentation guidelines
│   ├── TESTING_GUIDE.md            # Testing documentation
│   └── start.sh                    # Launch script
│
└── results/                      # Model results and analysis
    ├── MODEL_COMPARISON.md       # Detailed model comparison
    └── RESULTS_SUMMARY.md        # Quick results summary
```

## Quick Start

1. **Install Dependencies**:
   ```bash
   cd app/airbnb-forecasting-backend
   pip install -r requirements.txt
   
   cd ../airbnb-forecasting-frontend
   npm install
   ```

2. **Run the Application**:
   ```bash
   cd app/
   ./start.sh
   ```

3. **Access the App**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001

## Models

The project includes 6 forecasting models:
- **SARIMA**: Classical time series model
- **Prophet**: Meta's forecasting framework
- **LSTM**: Deep learning neural network
- **XGBoost**: Gradient boosting for price/occupancy
- **VAR/VECM**: Multi-variable time series
- **Ensemble**: Combined model (best performance)

**Best Model**: Ensemble achieves **2.87% MAPE** on 4-quarter forecasts.

## Documentation

- See [results/MODEL_COMPARISON.md](./results/MODEL_COMPARISON.md) for detailed model analysis
- See [results/RESULTS_SUMMARY.md](./results/RESULTS_SUMMARY.md) for quick reference
- See [app/QUICKSTART.md](./app/QUICKSTART.md) for getting started
- See [app/TESTING_GUIDE.md](./app/TESTING_GUIDE.md) for testing instructions

## Features

- 📊 Multi-model forecasting (SARIMA, Prophet, LSTM, XGBoost, VAR, Ensemble)
- 🗺️ Interactive map visualization
- 📈 Price and occupancy prediction
- 🎯 Extreme scenario analysis (Olympics, wildfires, regulations)
- 📱 Responsive design
- 🔄 Real-time forecasting

## Technology Stack

**Frontend**:
- React.js
- Recharts for visualization
- Leaflet for maps

**Backend**:
- Flask (Python)
- TensorFlow/Keras (LSTM)
- XGBoost
- Prophet
- Statsmodels (SARIMA, VAR)

## License

This project is for academic purposes (CMU Advanced AI Strategy Course).

---

**Last Updated**: December 2024
