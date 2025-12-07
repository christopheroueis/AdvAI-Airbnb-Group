"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import forecast, scenarios

app = FastAPI(
    title="Airbnb LA Forecasting API",
    description="ML-powered forecasting platform for LA home-sharing market",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(forecast.router, prefix="/api/forecast", tags=["forecasting"])
app.include_router(scenarios.router, prefix="/api/scenarios", tags=["scenarios"])

@app.get("/")
async def root():
    return {
        "message": "Airbnb LA Forecasting API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "forecast_volume": "/api/forecast/volume",
            "forecast_price": "/api/forecast/price",
            "forecast_occupancy": "/api/forecast/occupancy",
        }
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "models_loaded": True}
