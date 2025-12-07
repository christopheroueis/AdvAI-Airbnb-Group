"""
Scenario simulation API endpoints.
Allows users to run forecasts with different exogenous variable scenarios.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from app.ml.exogenous import get_exog_manager, ExogenousEventType
from app.ml.inference import get_forecast_service
import pandas as pd
import numpy as np

router = APIRouter()
exog_manager = get_exog_manager()
forecast_service = get_forecast_service()


class CustomShock(BaseModel):
    """Custom shock to apply in scenario."""
    period: str = Field(..., description="Period (e.g., '2024-Q3')")
    impact: float = Field(..., ge=-1.0, le=2.0, description="Impact as decimal (-1.0 to 2.0)")


class ScenarioRequest(BaseModel):
    """Request for scenario simulation."""
    scenario_id: Optional[str] = Field(None, description="ID of predefined scenario")
    scenario_name: Optional[str] = Field(None, description="Custom scenario name")
    events: List[str] = Field(default_factory=list, description="Event types to include")
    custom_shocks: List[CustomShock] = Field(default_factory=list)
    horizon: int = Field(4, ge=1, le=12, description="Forecast horizon in quarters")
    base_model: str = Field("ensemble", description="Base forecasting model")


class ScenarioResponse(BaseModel):
    """Response for scenario simulation."""
    scenario_name: str
    base_forecast: List[float]
    adjusted_forecast: List[float]
    total_impact_pct: List[float]
    summary: Dict
    periods: List[str]


class EventInfo(BaseModel):
    """Information about an exogenous event type."""
    event_type: str
    name: str
    description: str
    impact_multiplier: float
    historical_periods: Optional[List[Dict]]


@router.get("/scenarios", response_model=List[Dict])
async def get_available_scenarios():
    """
    Get list of predefined scenarios.
    
    Returns all available scenario templates that users can select.
    """
    scenarios = exog_manager.get_available_scenarios()
    return scenarios


@router.get("/events", response_model=List[EventInfo])
async def get_available_events():
    """
    Get list of available exogenous event types.
    
    Returns information about all event types that can be included in scenarios.
    """
    events = []
    for event_type in ExogenousEventType:
        info = exog_manager.get_event_info(event_type)
        if info:
            events.append(EventInfo(
                event_type=event_type.value,
                name=info.get("name", ""),
                description=info.get("description", ""),
                impact_multiplier=info.get("impact_multiplier", 0.0),
                historical_periods=info.get("historical_periods")
            ))
    return events


@router.post("/simulate", response_model=ScenarioResponse)
async def simulate_scenario(request: ScenarioRequest):
    """
    Simulate a forecast scenario with exogenous variables.
    
    Users can select:
    - Predefined scenarios (optimistic, pessimistic, etc.)
    - Custom combination of events (COVID, wildfires, weather)
    - Custom shocks for specific periods
    
    Returns both baseline and adjusted forecasts.
    """
    try:
        # Get base forecast (without exogenous variables)
        base_result = forecast_service.forecast_volume(
            horizon=request.horizon,
            model=request.base_model,
            include_intervals=False
        )
        base_forecast = np.array(base_result['forecast'])
        
        # Create date range for forecast (first day of each quarter)
        quarters = [f"2024Q{i}" if i <= 4 else f"2025Q{i-4}" 
                   for i in range(1, request.horizon + 1)]
        
        # Convert quarters to datetime (first day of quarter)
        date_list = []
        for q in quarters:
            year = int(q[:4])
            quarter = int(q[5:])
            # First month of quarter: Q1=Jan, Q2=Apr, Q3=Jul, Q4=Oct
            month = (quarter - 1) * 3 + 1
            date_list.append(pd.Timestamp(year=year, month=month, day=1))
        
        date_range = pd.DatetimeIndex(date_list)
        
        # Build scenario configuration
        if request.scenario_id:
            # Use predefined scenario
            predefined = next(
                (s for s in exog_manager.get_available_scenarios() 
                 if s['id'] == request.scenario_id),
                None
            )
            if not predefined:
                raise HTTPException(status_code=404, detail=f"Scenario '{request.scenario_id}' not found")
            
            scenario = predefined
        else:
            # Custom scenario
            # Convert string event types to enum
            event_enums = []
            for event_str in request.events:
                try:
                    event_enums.append(ExogenousEventType(event_str))
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid event type: {event_str}")
            
            scenario = {
                "name": request.scenario_name or "Custom Scenario",
                "events": event_enums,
                "custom_shocks": [{"period": s.period, "impact": s.impact} 
                                for s in request.custom_shocks]
            }
        
        # Simulate scenario
        result = exog_manager.simulate_scenario(
            base_forecast=base_forecast,
            date_range=date_range,
            scenario=scenario
        )
        
        # Format response
        return ScenarioResponse(
            scenario_name=result["scenario_name"],
            base_forecast=result["base_forecast"],
            adjusted_forecast=result["adjusted_forecast"],
            total_impact_pct=result["total_impact_pct"],
            summary=result["summary"],
            periods=quarters
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare", response_model=List[ScenarioResponse])
async def compare_scenarios(scenario_ids: List[str], horizon: int = 4):
    """
    Compare multiple predefined scenarios side-by-side.
    
    Args:
        scenario_ids: List of scenario IDs to compare
        horizon: Forecast horizon in quarters
    
    Returns:
        List of scenario results for comparison
    """
    results = []
    
    for scenario_id in scenario_ids:
        request = ScenarioRequest(
            scenario_id=scenario_id,
            horizon=horizon
        )
        result = await simulate_scenario(request)
        results.append(result)
    
    return results
