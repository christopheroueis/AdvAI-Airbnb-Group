"""
Forecasting API endpoints.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.forecast import (
    VolumeForecastRequest, VolumeForecastResponse,
    PriceForecastRequest, PriceForecastResponse,
    OccupancyForecastRequest, OccupancyForecastResponse,
    ForecastPoint
)
from app.ml.inference import ForecastService
from typing import List
import pandas as pd

router = APIRouter()
forecast_service = ForecastService()


@router.post("/volume", response_model=VolumeForecastResponse)
async def forecast_volume(request: VolumeForecastRequest):
    """
    Forecast listing volume for next N quarters.
    
    - **horizon**: Number of quarters to forecast (1-12)
    - **model**: Model to use (sarima, prophet, lstm, ensemble)
    - **include_confidence**: Include confidence intervals
    """
    try:
        result = forecast_service.forecast_volume(
            horizon=request.horizon,
            model=request.model.value,
            include_intervals=request.include_confidence
        )
        
        # Format response
        forecast_points = []
        quarters = [f"2024Q{i}" if i <= 4 else f"2025Q{i-4}" 
                   for i in range(1, request.horizon + 1)]
        
        for i, quarter in enumerate(quarters):
            point = ForecastPoint(
                period=quarter,
                value=float(result['forecast'][i]),
                ci_lower=float(result.get('ci_lower', [None]*len(quarters))[i]) if request.include_confidence else None,
                ci_upper=float(result.get('ci_upper', [None]*len(quarters))[i]) if request.include_confidence else None
            )
            forecast_points.append(point)
        
        return VolumeForecastResponse(
            forecast=forecast_points,
            model_used=request.model.value,
            metrics=result.get('metrics')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/price", response_model=PriceForecastResponse)
async def forecast_price(request: PriceForecastRequest):
    """
    Forecast optimal pricing for a property.
    
    Returns price recommendations based on property features and location.
    """
    try:
        result = forecast_service.forecast_price(
            room_type=request.room_type.value,
            neighborhood=request.neighborhood,
            bedrooms=request.bedrooms,
            bathrooms=request.bathrooms,
            accommodates=request.accommodates,
            amenities=request.amenities,
            horizon=request.horizon
        )
        
        # Format monthly forecasts
        forecast_points = []
        for i in range(request.horizon):
            month = pd.Timestamp('2024-01-01') + pd.DateOffset(months=i)
            point = ForecastPoint(
                period=month.strftime('%Y-%m'),
                value=float(result['forecast'][i]),
                ci_lower=float(result.get('ci_lower', [None]*request.horizon)[i]),
                ci_upper=float(result.get('ci_upper', [None]*request.horizon)[i])
            )
            forecast_points.append(point)
        
        return PriceForecastResponse(
            forecast=forecast_points,
            current_avg=float(result['current_avg']),
            recommended_price=float(result['recommended_price']),
            trend=result['trend'],
            seasonality_factor=result.get('seasonality_factor')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/occupancy", response_model=OccupancyForecastResponse)
async def forecast_occupancy(request: OccupancyForecastRequest):
    """
    Forecast occupancy rate and revenue for a property.
    
    Returns expected occupancy rates and revenue projections.
    """
    try:
        result = forecast_service.forecast_occupancy(
            room_type=request.room_type.value,
            neighborhood=request.neighborhood,
            bedrooms=request.bedrooms,
            bathrooms=request.bathrooms,
            accommodates=request.accommodates,
            amenities=request.amenities,
            price=request.price,
            horizon=request.horizon
        )
        
        return OccupancyForecastResponse(
            forecast=result['forecast'],
            expected_bookings_per_month=float(result['bookings_per_month']),
            revenue_estimate=float(result['revenue_estimate'])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
