"""
GR Race Strategist AI - FastAPI Backend
Main application entry point with health check and API routes
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import pandas as pd
import io

# Import our modules
from models import (
    TireWearIndex, DriverConsistencyScore, TrafficLossFactor,
    TrackEvolutionRate, PaceDeltaTrend, StrategyResponse,
    PitWindowRecommendation, UndercutSimulation, PaceProjection
)
from data_loader import RaceDataLoader
from feature_engineering import FeatureEngineer
from ml_models import RaceStrategyPredictor
from trd_data_loader import TRDDataLoader
import numpy as np

# Initialize FastAPI app
app = FastAPI(
    title="GR Race Strategist AI",
    description="Real-time race strategy prediction system for Toyota GR",
    version="1.0.0"
)

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://toyota-gr.vercel.app",  # Production Vercel URL
        "https://toyota-gr-muhammed-idris-projects.vercel.app",  # Vercel team URL
        "https://toyota-gr-git-main-muhammed-idris-projects.vercel.app",  # Vercel branch URL
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel preview deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global state (in production, use proper state management)
data_loader: Optional[RaceDataLoader] = None
feature_engineer: Optional[FeatureEngineer] = None
strategy_predictor: Optional[RaceStrategyPredictor] = None

# Response models
class HealthResponse(BaseModel):
    status: str
    message: str
    version: str


# Routes
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "GR Race Strategist AI API",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify backend is running
    """
    return HealthResponse(
        status="healthy",
        message="Backend is running successfully",
        version="1.0.0"
    )


@app.get("/api/status", tags=["API"])
async def api_status():
    """API status endpoint"""
    return {
        "api": "GR Race Strategist AI",
        "status": "operational",
        "data_loaded": data_loader is not None,
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "api": "/api/status"
        }
    }


# ============================================================================
# Data Loading Endpoints
# ============================================================================

# REMOVED: Sample data and upload endpoints
# This application ONLY uses real-time TRD hackathon data from Data-GR folder
# No mock, sample, or AI-generated data is allowed


@app.post("/api/data/load-trd", tags=["Data"])
async def load_trd_data(track: str, race: str = "Race 1", data_root: Optional[str] = None):
    """
    Load REAL-TIME TRD hackathon dataset from Data-GR folder
    
    This is the ONLY data loading method. No mock, sample, or AI-generated data is allowed.
    All data must come from the TRD hackathon datasets.
    
    Args:
        track: Track name (e.g., "COTA", "Sonoma", "barber")
        race: Race number ("Race 1" or "Race 2")
        data_root: Root directory of Data-GR folder (default: Data-GR, located in backend/)
    """
    global data_loader, feature_engineer, strategy_predictor
    
    try:
        # Default data root (relative to backend folder)
        # Use Data-GR-minimal by default (deployed to Render), fall back to Data-GR for local dev
        from pathlib import Path
        if data_root is None:
            # Try Data-GR-minimal first (deployed version), then Data-GR (local dev)
            if Path("Data-GR-minimal").exists():
                data_root = "Data-GR-minimal"
            elif Path("Data-GR").exists():
                data_root = "Data-GR"
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Neither Data-GR-minimal nor Data-GR folder found. Please ensure the dataset folder exists."
                )
        
        # Validate data folder exists
        data_path = Path(data_root)
        if not data_path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Data folder not found at {data_root}. This application requires real-time TRD hackathon data. Please ensure the dataset folder exists with the hackathon datasets."
            )
        
        # Initialize TRD loader
        trd_loader = TRDDataLoader(data_root=data_root)
        
        # Load analysis file
        df = trd_loader.load_analysis_file(track=track, race=race)
        
        # Combine with results for position data
        df = trd_loader.combine_with_results(track=track, race=race)
        
        # Get normalized data
        normalized_df = trd_loader.get_normalized_data()
        
        # Load into standard data loader
        data_loader = RaceDataLoader()
        data_loader.load_from_dataframe(normalized_df)
        
        # Initialize feature engineer
        feature_engineer = FeatureEngineer(normalized_df)
        
        # Initialize strategy predictor
        strategy_predictor = RaceStrategyPredictor(feature_engineer)
        
        # Validate
        validation = data_loader.validate_data()
        
        # Convert numpy types to native Python types for JSON serialization
        drivers_list = [str(d) for d in normalized_df['driver_id'].unique().tolist()]
        min_lap = int(normalized_df['lap_number'].min())
        max_lap = int(normalized_df['lap_number'].max())
        
        # Convert validation dict values to native types
        validation_clean = {}
        for key, value in validation.items():
            if isinstance(value, (np.integer, np.floating)):
                validation_clean[key] = int(value) if isinstance(value, np.integer) else float(value)
            elif isinstance(value, bool):
                validation_clean[key] = bool(value)
            else:
                validation_clean[key] = value
        
        return {
            "status": "success",
            "message": f"Loaded TRD data: {track} - {race}",
            "track": track,
            "race": race,
            "drivers": drivers_list,
            "total_laps": int(len(normalized_df)),
            "lap_range": {
                "min": min_lap,
                "max": max_lap
            },
            "validation": validation_clean
        }
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/api/data/trd/tracks", tags=["Data"])
async def list_trd_tracks(data_root: Optional[str] = None):
    """List all available tracks in TRD dataset (REAL-TIME TRD data only)"""
    try:
        # Use Data-GR-minimal by default (deployed to Render), fall back to Data-GR for local dev
        from pathlib import Path
        if data_root is None:
            if Path("Data-GR-minimal").exists():
                data_root = "Data-GR-minimal"
            elif Path("Data-GR").exists():
                data_root = "Data-GR"
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Neither Data-GR-minimal nor Data-GR folder found. Please ensure the dataset folder exists."
                )
        
        # Validate data folder exists
        data_path = Path(data_root)
        if not data_path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Data folder not found at {data_root}. This application requires real-time TRD hackathon data. Please ensure the dataset folder exists with the hackathon datasets."
            )
        
        trd_loader = TRDDataLoader(data_root=data_root)
        tracks = trd_loader.list_available_tracks()
        return {
            "tracks": tracks,
            "count": len(tracks)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/trd/races/{track}", tags=["Data"])
async def list_trd_races(track: str, data_root: Optional[str] = None):
    """List available races for a track (REAL-TIME TRD data only)"""
    try:
        # Use Data-GR-minimal by default (deployed to Render), fall back to Data-GR for local dev
        from pathlib import Path
        if data_root is None:
            if Path("Data-GR-minimal").exists():
                data_root = "Data-GR-minimal"
            elif Path("Data-GR").exists():
                data_root = "Data-GR"
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Neither Data-GR-minimal nor Data-GR folder found. Please ensure the dataset folder exists."
                )
        
        # Validate data folder exists
        data_path = Path(data_root)
        if not data_path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Data folder not found at {data_root}. This application requires real-time TRD hackathon data. Please ensure the dataset folder exists with the hackathon datasets."
            )
        
        trd_loader = TRDDataLoader(data_root=data_root)
        races = trd_loader.list_races_for_track(track)
        return {
            "track": track,
            "races": races,
            "count": len(races)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/info", tags=["Data"])
async def get_data_info():
    """Get information about loaded data"""
    if data_loader is None:
        raise HTTPException(status_code=404, detail="No data loaded. Use /api/data/load-trd to load real-time TRD hackathon data from Data-GR folder")
    
    validation = data_loader.validate_data()
    
    # Convert numpy types to native Python types
    validation_clean = {}
    for key, value in validation.items():
        if isinstance(value, (np.integer, np.floating)):
            validation_clean[key] = int(value) if isinstance(value, np.integer) else float(value)
        elif isinstance(value, bool):
            validation_clean[key] = bool(value)
        else:
            validation_clean[key] = value
    
    if data_loader.lap_data is not None:
        drivers = [str(d) for d in data_loader.lap_data['driver_id'].unique().tolist()]
        lap_range = {
            "min": int(data_loader.lap_data['lap_number'].min()),
            "max": int(data_loader.lap_data['lap_number'].max())
        }
    else:
        drivers = []
        lap_range = {}
    
    return {
        "loaded": True,
        "drivers": drivers,
        "lap_range": lap_range,
        "validation": validation_clean
    }


# ============================================================================
# Feature Engineering Endpoints
# ============================================================================

@app.get("/api/features/tire-wear/{driver_id}", response_model=TireWearIndex, tags=["Features"])
async def get_tire_wear(driver_id: str, current_lap: Optional[int] = None):
    """Get Tire Wear Index for a driver"""
    if feature_engineer is None:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    try:
        return feature_engineer.calculate_tire_wear_index(driver_id, current_lap)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/features/consistency/{driver_id}", response_model=DriverConsistencyScore, tags=["Features"])
async def get_consistency(driver_id: str, window: int = 10):
    """Get driver consistency score"""
    if feature_engineer is None:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    try:
        return feature_engineer.calculate_consistency_score(driver_id, window)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/features/traffic/{driver_id}", response_model=TrafficLossFactor, tags=["Features"])
async def get_traffic_loss(driver_id: str, current_lap: Optional[int] = None):
    """Get traffic loss factor for a driver"""
    if feature_engineer is None:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    try:
        return feature_engineer.calculate_traffic_loss(driver_id, current_lap)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/features/track-evolution", response_model=TrackEvolutionRate, tags=["Features"])
async def get_track_evolution(window: int = 20):
    """Get track evolution rate"""
    if feature_engineer is None:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    try:
        return feature_engineer.calculate_track_evolution(window)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/features/pace-delta/{driver_id}", response_model=PaceDeltaTrend, tags=["Features"])
async def get_pace_delta(driver_id: str, window: int = 10):
    """Get pace delta trend for a driver"""
    if feature_engineer is None:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    try:
        return feature_engineer.calculate_pace_delta_trend(driver_id, window=window)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Strategy Prediction Endpoints
# ============================================================================

@app.get("/api/strategy/{driver_id}", response_model=StrategyResponse, tags=["Strategy"])
async def get_strategy(
    driver_id: str,
    current_lap: int,
    total_laps: int = 50,
    include_undercut: bool = True
):
    """
    Get complete strategy recommendation for a driver
    
    Args:
        driver_id: Driver identifier
        current_lap: Current lap number
        total_laps: Total race laps
        include_undercut: Whether to include undercut analysis
    """
    if strategy_predictor is None:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    try:
        # Get all features
        tire_wear = feature_engineer.calculate_tire_wear_index(driver_id, current_lap)
        consistency = feature_engineer.calculate_consistency_score(driver_id)
        traffic_loss = feature_engineer.calculate_traffic_loss(driver_id, current_lap)
        
        # Get predictions
        pit_window = strategy_predictor.predict_pit_window(driver_id, current_lap, total_laps)
        pace_projection = strategy_predictor.project_pace(driver_id, current_lap)
        
        # Get undercut opportunities
        undercut_opportunities = []
        if include_undercut:
            # Find other drivers
            all_drivers = data_loader.lap_data['driver_id'].unique()
            for target_id in all_drivers:
                if target_id != driver_id:
                    try:
                        undercut = strategy_predictor.simulate_undercut(
                            driver_id, target_id, current_lap, total_laps
                        )
                        if undercut.success_probability > 0.5:  # Only show viable opportunities
                            undercut_opportunities.append(undercut)
                    except:
                        continue
        
        return StrategyResponse(
            driver_id=driver_id,
            tire_wear=tire_wear,
            pace_projection=pace_projection,
            pit_window=pit_window,
            undercut_opportunities=undercut_opportunities,
            consistency=consistency,
            traffic_loss=traffic_loss
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/strategy/pit-window/{driver_id}", response_model=PitWindowRecommendation, tags=["Strategy"])
async def get_pit_window(driver_id: str, current_lap: int, total_laps: int = 50):
    """Get pit window recommendation"""
    if strategy_predictor is None:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    try:
        return strategy_predictor.predict_pit_window(driver_id, current_lap, total_laps)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/strategy/undercut/{driver_id}/{target_driver_id}", response_model=UndercutSimulation, tags=["Strategy"])
async def get_undercut(driver_id: str, target_driver_id: str, current_lap: int, total_laps: int = 50):
    """Get undercut/overcut simulation"""
    if strategy_predictor is None:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    try:
        return strategy_predictor.simulate_undercut(driver_id, target_driver_id, current_lap, total_laps)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/strategy/pace-projection/{driver_id}", response_model=PaceProjection, tags=["Strategy"])
async def get_pace_projection(driver_id: str, current_lap: int, projection_laps: int = 10):
    """Get pace projection"""
    if strategy_predictor is None:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    try:
        return strategy_predictor.project_pace(driver_id, current_lap, projection_laps)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Main entry point for development
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )

