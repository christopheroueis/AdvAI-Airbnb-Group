# Model Training Results Summary

## Quick Reference

### Best Model by Task

| Task | Model | MAPE | RMSE | Notes |
|------|-------|------|------|-------|
| **Volume Forecast (1Q)** | LSTM | 0.67% | 298 | Highest 1-step accuracy |
| **Volume Forecast (4Q)** | Ensemble | 2.87% | 772 | Best multi-step performance |
| **Price Prediction** | XGBoost | 18.7% | $42.18 | Requires property features |
| **Occupancy Forecast** | XGBoost | 13.6% | 0.142 | 67% R² |

### All Models Performance (Volume Forecasting)

```
Model      | MAPE ↓  | RMSE ↓ | MAE ↓ | R²  ↑  | Training Time
-----------|---------|--------|-------|--------|---------------
Ensemble   | 2.87%   | 772    | 651   | 0.956  | 130.7s
LSTM       | 3.15%   | 823    | 697   | 0.941  | 118.6s
Prophet    | 3.52%   | 967    | 831   | 0.908  | 7.3s
XGBoost    | 3.64%   | 956    | 814   | 0.912  | 12.4s
SARIMA     | 3.87%   | 1,024  | 892   | 0.891  | 4.8s
VAR/VECM   | 4.12%   | 1,129  | 973   | 0.867  | 9.2s
```

**🏆 Winner**: Ensemble (2.87% MAPE)

## Feature Importance (XGBoost Price Model)

```
1. neighborhood_cleansed     24.5%  ████████████
2. bedrooms                  18.3%  █████████
3. accommodates              14.2%  ███████
4. amenities_count            9.8%  █████
5. bathrooms                  8.7%  ████
6. is_superhost               6.2%  ███
7. coastal                    5.5%  ███
8. has_pool                   4.8%  ██
9. quarter_num                4.1%  ██
10. competition_index         3.9%  ██
```

## Key Insights

1. **Ensemble is 9% more accurate** than best individual model
2. **LSTM excels** at 1-step forecasting (0.67% error)
3. **Prophet is fastest** for production (7.3s training)
4. **Location dominates** price predictions (24.5% importance)
5. **All models achieve MAPE < 5%** (excellent accuracy)

See full analysis in [MODEL_COMPARISON.md](./MODEL_COMPARISON.md)
