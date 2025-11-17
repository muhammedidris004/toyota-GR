"""
Data models and schemas for GR Race Strategist AI
Defines the structure of racing data and API request/response models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


# ============================================================================
# Core Racing Data Models
# ============================================================================

class LapData(BaseModel):
    """Single lap data point"""
    lap_number: int
    driver_id: str
    lap_time: float = Field(..., description="Lap time in seconds")
    sector_1_time: Optional[float] = None
    sector_2_time: Optional[float] = None
    sector_3_time: Optional[float] = None
    tire_compound: str = Field(..., description="Soft, Medium, Hard")
    tire_age: int = Field(..., description="Number of laps on current tires")
    fuel_load: Optional[float] = Field(None, description="Fuel load in kg")
    position: int
    track_temperature: Optional[float] = None
    air_temperature: Optional[float] = None
    timestamp: Optional[datetime] = None


class DriverData(BaseModel):
    """Driver performance data"""
    driver_id: str
    driver_name: Optional[str] = None
    current_position: int
    current_tire_compound: str
    current_tire_age: int
    total_laps: int
    best_lap_time: float
    average_lap_time: float
    consistency_score: Optional[float] = None


class RaceState(BaseModel):
    """Current race state"""
    race_lap: int
    total_laps: int
    session_time: float
    track_evolution_rate: Optional[float] = None
    safety_car_deployed: bool = False
    weather_condition: str = "dry"  # dry, wet, mixed


# ============================================================================
# Feature Engineering Output Models
# ============================================================================

class TireWearIndex(BaseModel):
    """Tire Wear Index calculation"""
    driver_id: str
    current_twi: float = Field(..., description="Current Tire Wear Index (0-100)")
    projected_twi: float = Field(..., description="Projected TWI after N laps")
    degradation_rate: float = Field(..., description="TWI degradation per lap")
    optimal_pit_lap: Optional[int] = Field(None, description="Recommended pit lap")


class DriverConsistencyScore(BaseModel):
    """Driver consistency metrics"""
    driver_id: str
    consistency_score: float = Field(..., description="0-100, higher = more consistent")
    lap_time_variance: float
    sector_variance: Dict[str, float]
    recent_trend: str = Field(..., description="improving, stable, degrading")


class TrafficLossFactor(BaseModel):
    """Traffic impact on lap time"""
    driver_id: str
    traffic_loss: float = Field(..., description="Time lost due to traffic (seconds)")
    cars_ahead: int
    dirty_air_factor: float = Field(..., description="Aerodynamic impact (0-1)")
    overtake_opportunity: bool


class TrackEvolutionRate(BaseModel):
    """Track condition evolution"""
    evolution_rate: float = Field(..., description="Lap time improvement per lap (negative = faster)")
    track_grip_level: float = Field(..., description="0-100, higher = more grip")
    rubber_laying_effect: float = Field(..., description="Cumulative rubber effect")
    projected_optimal_lap: Optional[int] = None


class PaceDeltaTrend(BaseModel):
    """Pace delta analysis"""
    driver_id: str
    current_pace_delta: float = Field(..., description="Delta to reference pace (seconds)")
    pace_trend: List[float] = Field(..., description="Pace delta over last N laps")
    trend_direction: str = Field(..., description="improving, stable, degrading")
    projected_pace: float = Field(..., description="Projected pace in N laps")


# ============================================================================
# Strategy Prediction Models
# ============================================================================

class PitWindowRecommendation(BaseModel):
    """Pit stop window recommendation"""
    driver_id: str
    optimal_pit_lap: int
    pit_window_start: int
    pit_window_end: int
    urgency: str = Field(..., description="low, medium, high, critical")
    reason: str
    estimated_time_loss: float = Field(..., description="Time lost if pitting outside window")
    tire_compound_recommendation: str


class UndercutSimulation(BaseModel):
    """Undercut/overcut opportunity analysis"""
    driver_id: str
    target_driver_id: str
    strategy_type: str = Field(..., description="undercut, overcut")
    optimal_pit_lap: int
    expected_gain: float = Field(..., description="Expected position/time gain")
    success_probability: float = Field(..., description="0-1 probability of success")
    risk_factors: List[str]


class PaceProjection(BaseModel):
    """Lap pace projection"""
    driver_id: str
    current_lap: int
    projected_laps: List[Dict[str, float]] = Field(..., description="List of {lap: X, pace: Y}")
    factors_considered: List[str]
    confidence: float = Field(..., description="0-1 confidence in projection")


# ============================================================================
# API Request/Response Models
# ============================================================================

class RaceDataRequest(BaseModel):
    """Request to process race data"""
    lap_data: List[LapData]
    race_state: RaceState
    drivers: List[DriverData]


class StrategyRequest(BaseModel):
    """Request for strategy recommendations"""
    driver_id: str
    current_lap: int
    race_state: RaceState
    include_undercut: bool = True


class StrategyResponse(BaseModel):
    """Complete strategy response"""
    driver_id: str
    tire_wear: TireWearIndex
    pace_projection: PaceProjection
    pit_window: PitWindowRecommendation
    undercut_opportunities: List[UndercutSimulation]
    consistency: DriverConsistencyScore
    traffic_loss: TrafficLossFactor

