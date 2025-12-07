"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class ModelType(str, Enum):
    """Available forecasting models."""
    SARIMA = "sarima"
    PROPHET = "prophet"
    LSTM = "lstm"
    XGBOOST = "xgboost"
    ENSEMBLE = "ensemble"


class RoomType(str, Enum):
    """Airbnb room types."""
    ENTIRE_HOME = "Entire home/apt"
    PRIVATE_ROOM = "Private room"
    HOTEL_ROOM = "Hotel room"
    SHARED_ROOM = "Shared room"


# Forecast Requests/Responses

class VolumeForecastRequest(BaseModel):
    """Request for listing volume forecast."""
    horizon: int = Field(4, ge=1, le=12, description="Number of quarters to forecast")
    model: ModelType = Field(ModelType.ENSEMBLE, description="Model to use for forecasting")
    include_confidence: bool = Field(True, description="Include confidence intervals")


class ForecastPoint(BaseModel):
    """Single forecast data point."""
    period: str = Field(..., description="Time period (e.g., '2024Q1')")
    value: float = Field(..., description="Forecasted value")
    ci_lower: Optional[float] = Field(None, description="Lower confidence interval")
    ci_upper: Optional[float] = Field(None, description="Upper confidence interval")


class VolumeForecastResponse(BaseModel):
    """Response for listing volume forecast."""
    forecast: List[ForecastPoint]
    model_used: str
    metrics: Optional[Dict[str, float]] = None


class PriceForecastRequest(BaseModel):
    """Request for price forecast."""
    room_type: RoomType
    neighborhood: str
    bedrooms: int = Field(..., ge=0, le=10)
    bathrooms: Optional[float] = Field(None, ge=0, le=10)
    accommodates: Optional[int] = Field(None, ge=1, le=16)
    amenities: List[str] = Field(default_factory=list)
    horizon: int = Field(12, ge=1, le=24, description="Number of months to forecast")


class PriceForecastResponse(BaseModel):
    """Response for price forecast."""
    forecast: List[ForecastPoint]
    current_avg: float
    recommended_price: float
    trend: str  # "increasing", "decreasing", "stable"
    seasonality_factor: Optional[float] = None


class OccupancyForecastRequest(BaseModel):
    """Request for occupancy rate forecast."""
    room_type: RoomType
    neighborhood: str
    bedrooms: int
    bathrooms: Optional[float] = None
    accommodates: Optional[int] = None
    amenities: List[str] = Field(default_factory=list)
    price: float = Field(..., gt=0)
    horizon: int = Field(6, ge=1, le=12, description="Number of months to forecast")


class OccupancyForecastPoint(BaseModel):
    """Single occupancy forecast data point."""
    month: str = Field(..., description="Month in YYYY-MM format")
    occupancy_rate: float = Field(..., description="Predicted occupancy rate (0-1)")


class OccupancyForecastResponse(BaseModel):
    """Response for occupancy forecast."""
    forecast: List[OccupancyForecastPoint]
    expected_bookings_per_month: float
    revenue_estimate: float


# Insights Requests/Responses

class NeighborhoodRecommendationRequest(BaseModel):
    """Request for neighborhood recommendations."""
    room_type: Optional[RoomType] = None
    max_price: Optional[float] = Field(None, gt=0, description="Maximum nightly price")
    min_bedrooms: Optional[int] = Field(None, ge=0)
    top_n: int = Field(5, ge=1, le=20, description="Number of recommendations")


class NeighborhoodRecommendation(BaseModel):
    """Single neighborhood recommendation."""
    neighborhood: str
    score: float = Field(..., ge=0, le=100, description="Composite score 0-100")
    avg_price: float
    avg_occupancy: float
    competition: str  # "low", "moderate", "high"
    growth_rate: float
    reasoning: str


class NeighborhoodRecommendationResponse(BaseModel):
    """Response for neighborhood recommendations."""
    recommendations: List[NeighborhoodRecommendation]
    total_neighborhoods_analyzed: int


class PricingRecommendationRequest(BaseModel):
    """Request for pricing recommendation."""
    room_type: RoomType
    neighborhood: str
    bedrooms: int
    bathrooms: Optional[float] = None
    accommodates: Optional[int] = None
    amenities: List[str] = Field(default_factory=list)


class PricingRecommendationResponse(BaseModel):
    """Response for pricing recommendation."""
    recommended_price: float
    price_range: Dict[str, float]  # {min: float, max: float}
    comparable_listings: int
    percentile_50: float  # Median price
    percentile_75: float
    factors: Dict[str, float]  # Price adjustments by factor


# Model Management

class ModelInfo(BaseModel):
    """Information about a trained model."""
    name: str
    version: str
    last_trained: str  # ISO date
    metrics: Dict[str, float]
    status: str  # "production", "testing", "deprecated"


class ModelStatusResponse(BaseModel):
    """Response for model status endpoint."""
    models: List[ModelInfo]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    models_loaded: int
