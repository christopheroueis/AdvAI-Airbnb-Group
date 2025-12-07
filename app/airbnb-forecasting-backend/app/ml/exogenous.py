"""
Exogenous variables for scenario simulation.
Allows users to include external events (COVID, wildfires, weather) in forecasts.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class ExogenousEventType(str, Enum):
    """Types of exogenous events."""
    COVID_19 = "covid_19"
    WILDFIRE = "wildfire"
    EXTREME_WEATHER = "extreme_weather"
    ECONOMIC_RECESSION = "economic_recession"
    MAJOR_EVENT = "major_event"  # Olympics, concerts, etc.
    REGULATORY_CHANGE = "regulatory_change"


class ExogenousVariableManager:
    """Manage exogenous variables for scenario simulation."""
    
    def __init__(self):
        self.event_definitions = self._define_events()
        
    def _define_events(self) -> Dict:
        """Define historical and potential future events."""
        return {
            ExogenousEventType.COVID_19: {
                "name": "COVID-19 Pandemic",
                "description": "Impact of COVID-19 on travel and short-term rentals",
                "historical_periods": [
                    {"start": "2020-03", "end": "2021-06", "severity": 0.8},  # High impact
                    {"start": "2021-07", "end": "2022-12", "severity": 0.4},  # Recovery
                ],
                "impact_multiplier": -0.6,  # -60% listings at peak
            },
            ExogenousEventType.WILDFIRE: {
                "name": "LA Wildfires",
                "description": "Major wildfire events affecting LA area",
                "historical_periods": [
                    {"start": "2020-08", "end": "2020-10", "severity": 0.6},
                    {"start": "2023-07", "end": "2023-08", "severity": 0.4},
                ],
                "impact_multiplier": -0.3,  # -30% during active fires
                "affected_neighborhoods": ["Malibu", "Topanga", "Hollywood Hills"],
            },
            ExogenousEventType.EXTREME_WEATHER: {
                "name": "Extreme Weather Events",
                "description": "Heat waves, storms, atmospheric rivers",
                "seasonal_pattern": {
                    "Q1": 0.3,  # Winter storms
                    "Q2": 0.2,
                    "Q3": 0.5,  # Heat waves
                    "Q4": 0.2,
                },
                "impact_multiplier": -0.15,  # -15% during extreme events
            },
            ExogenousEventType.ECONOMIC_RECESSION: {
                "name": "Economic Recession",
                "description": "Economic downturn affecting travel spending",
                "historical_periods": [
                    {"start": "2008-01", "end": "2009-12", "severity": 0.9},
                    {"start": "2020-03", "end": "2020-06", "severity": 0.7},
                ],
                "impact_multiplier": -0.4,  # -40% during recession
            },
            ExogenousEventType.MAJOR_EVENT: {
                "name": "Major Events (Olympics, Concerts, etc.)",
                "description": "Large events driving tourism",
                "historical_periods": [
                    {"start": "2028-07", "end": "2028-08", "severity": 1.0},  # 2028 LA Olympics
                ],
                "impact_multiplier": 0.5,  # +50% during major events
            },
            ExogenousEventType.REGULATORY_CHANGE: {
                "name": "Airbnb Regulation Changes",
                "description": "New laws restricting or enabling short-term rentals",
                "historical_periods": [
                    {"start": "2019-01", "end": "2019-12", "severity": 0.6},  # LA regulations
                ],
                "impact_multiplier": -0.25,  # -25% with restrictions
            },
        }
    
    def create_exogenous_features(self, date_range: pd.DatetimeIndex,
                                  enabled_events: List[ExogenousEventType]) -> pd.DataFrame:
        """
        Create exogenous variable features for given date range.
        
        Args:
            date_range: DatetimeIndex of prediction periods
            enabled_events: List of event types to include
            
        Returns:
            DataFrame with exogenous variable columns
        """
        df = pd.DataFrame(index=date_range)
        
        for event_type in enabled_events:
            event_def = self.event_definitions[event_type]
            feature_name = f"exog_{event_type.value}"
            
            # Initialize with zeros
            df[feature_name] = 0.0
            
            # Apply historical periods
            if "historical_periods" in event_def:
                for period in event_def["historical_periods"]:
                    start = pd.to_datetime(period["start"])
                    end = pd.to_datetime(period["end"])
                    severity = period["severity"]
                    
                    # Mark affected dates
                    mask = (df.index >= start) & (df.index <= end)
                    df.loc[mask, feature_name] = severity * event_def["impact_multiplier"]
            
            # Apply seasonal patterns
            if "seasonal_pattern" in event_def:
                for quarter, intensity in event_def["seasonal_pattern"].items():
                    quarter_num = int(quarter.replace("Q", ""))
                    # Find matching quarters
                    mask = df.index.quarter == quarter_num
                    if mask.any():
                        df.loc[mask, feature_name] = intensity * event_def["impact_multiplier"]
        
        return df
    
    def simulate_scenario(self, base_forecast: np.ndarray,
                         date_range: pd.DatetimeIndex,
                         scenario: Dict[str, any]) -> Dict:
        """
        Simulate a scenario with selected exogenous events.
        
        Args:
            base_forecast: Baseline forecast without exogenous variables
            date_range: DatetimeIndex of forecast periods
            scenario: Dictionary with scenario configuration
                {
                    "name": "Scenario name",
                    "events": [ExogenousEventType.COVID_19, ...],
                    "custom_shocks": [{"period": "2024-Q3", "impact": -0.2}]
                }
        
        Returns:
            Dictionary with adjusted forecast and scenario details
        """
        # Create exogenous features
        exog_df = self.create_exogenous_features(date_range, scenario.get("events", []))
        
        # Calculate total impact
        total_impact = exog_df.sum(axis=1).values
        
        # Apply custom shocks
        if "custom_shocks" in scenario:
            for shock in scenario["custom_shocks"]:
                period = shock["period"]
                impact = shock["impact"]
                # Find matching period
                # (simplified - assumes period matches date_range format)
                total_impact += impact
        
        # Adjust forecast
        adjusted_forecast = base_forecast * (1 + total_impact)
        
        # Calculate impact summary
        avg_impact = np.mean(total_impact)
        max_negative = np.min(total_impact)
        max_positive = np.max(total_impact)
        
        return {
            "scenario_name": scenario.get("name", "Unnamed Scenario"),
            "base_forecast": base_forecast.tolist(),
            "adjusted_forecast": adjusted_forecast.tolist(),
            "total_impact_pct": (total_impact * 100).tolist(),
            "summary": {
                "avg_impact_pct": avg_impact * 100,
                "max_negative_impact_pct": max_negative * 100,
                "max_positive_impact_pct": max_positive * 100,
                "events_included": [e.value for e in scenario.get("events", [])],
            },
            "exogenous_features": exog_df.to_dict()
        }
    
    def get_available_scenarios(self) -> List[Dict]:
        """Get predefined scenario templates."""
        return [
            {
                "id": "optimistic",
                "name": "Optimistic Growth",
                "description": "Major events drive tourism, no major disruptions",
                "events": [ExogenousEventType.MAJOR_EVENT],
                "custom_shocks": [],
            },
            {
                "id": "baseline",
                "name": "Baseline (Status Quo)",
                "description": "Normal market conditions",
                "events": [],
                "custom_shocks": [],
            },
            {
                "id": "pessimistic",
                "name": "Pessimistic (Multiple Disruptions)",
                "description": "Economic downturn + wildfires + extreme weather",
                "events": [
                    ExogenousEventType.ECONOMIC_RECESSION,
                    ExogenousEventType.WILDFIRE,
                    ExogenousEventType.EXTREME_WEATHER
                ],
                "custom_shocks": [],
            },
            {
                "id": "wildfire_season",
                "name": "Severe Wildfire Season",
                "description": "Extended wildfire season affecting LA",
                "events": [ExogenousEventType.WILDFIRE],
                "custom_shocks": [
                    {"period": "2024-Q3", "impact": -0.35},
                    {"period": "2024-Q4", "impact": -0.20}
                ],
            },
            {
                "id": "olympics_2028",
                "name": "2028 LA Olympics",
                "description": "Surge in demand for 2028 Olympics",
                "events": [ExogenousEventType.MAJOR_EVENT],
                "custom_shocks": [
                    {"period": "2028-Q2", "impact": 0.6},
                    {"period": "2028-Q3", "impact": 0.8}
                ],
            },
            {
                "id": "regulatory_crackdown",
                "name": "Strict Regulation",
                "description": "New laws restrict short-term rentals",
                "events": [ExogenousEventType.REGULATORY_CHANGE],
                "custom_shocks": [
                    {"period": "2024-Q1", "impact": -0.30}
                ],
            },
        ]
    
    def get_event_info(self, event_type: ExogenousEventType) -> Dict:
        """Get detailed information about an event type."""
        return self.event_definitions.get(event_type, {})


# Singleton instance
_exog_manager = None

def get_exog_manager() -> ExogenousVariableManager:
    """Get or create exogenous variable manager singleton."""
    global _exog_manager
    if _exog_manager is None:
        _exog_manager = ExogenousVariableManager()
    return _exog_manager
