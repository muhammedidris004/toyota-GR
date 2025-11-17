"""
ML Models for GR Race Strategist AI
Predictions for tire wear, pace, pit windows, and undercut opportunities
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
from pathlib import Path

from models import (
    PitWindowRecommendation, UndercutSimulation, PaceProjection
)
from feature_engineering import FeatureEngineer


class RaceStrategyPredictor:
    """
    Main prediction engine for race strategy
    Combines feature engineering with ML models
    """
    
    def __init__(self, feature_engineer: FeatureEngineer):
        """
        Initialize predictor with feature engineer
        
        Args:
            feature_engineer: FeatureEngineer instance with loaded data
        """
        self.fe = feature_engineer
        self.tire_wear_model = None
        self.pace_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models (can be trained or use rule-based for now)"""
        # For hackathon, we'll use rule-based + simple ML
        # In production, these would be trained on historical data
        self.tire_wear_model = None  # Using rule-based for now
        self.pace_model = None  # Using rule-based for now
    
    def _calculate_adaptive_degradation_rate(
        self,
        driver_id: str,
        tire_compound: str,
        tire_age: int,
        current_lap: int
    ) -> float:
        """
        Calculate adaptive degradation rate based on real data patterns
        
        Uses historical data to adjust degradation rates
        """
        driver_laps = self.fe.lap_data[self.fe.lap_data['driver_id'] == driver_id]
        
        if len(driver_laps) < 5:
            # Not enough data, use default
            base_rates = {'Soft': 2.5, 'Medium': 1.5, 'Hard': 1.0}
            return base_rates.get(tire_compound, 1.5)
        
        # Calculate actual degradation from data
        recent_laps = driver_laps[driver_laps['lap_number'] <= current_lap].tail(10)
        
        if len(recent_laps) < 3:
            base_rates = {'Soft': 2.5, 'Medium': 1.5, 'Hard': 1.0}
            return base_rates.get(tire_compound, 1.5)
        
        # Calculate pace degradation (how much slower per lap)
        lap_times = recent_laps['lap_time'].values
        if len(lap_times) >= 3:
            # Linear regression to find degradation rate
            x = np.arange(len(lap_times))
            slope = np.polyfit(x, lap_times, 1)[0]  # Linear fit slope
            
            # Convert pace degradation to TWI degradation
            # Assuming 0.1s pace loss = 1 TWI point
            adaptive_rate = abs(slope) * 10
            
            # Blend with base rate (70% adaptive, 30% base)
            base_rates = {'Soft': 2.5, 'Medium': 1.5, 'Hard': 1.0}
            base_rate = base_rates.get(tire_compound, 1.5)
            
            return 0.7 * adaptive_rate + 0.3 * base_rate
        
        base_rates = {'Soft': 2.5, 'Medium': 1.5, 'Hard': 1.0}
        return base_rates.get(tire_compound, 1.5)
    
    # ========================================================================
    # Pit Window Recommendation
    # ========================================================================
    
    def predict_pit_window(
        self,
        driver_id: str,
        current_lap: int,
        total_laps: int
    ) -> PitWindowRecommendation:
        """
        Predict optimal pit window for a driver
        
        Args:
            driver_id: Driver identifier
            current_lap: Current lap number
            total_laps: Total race laps
            
        Returns:
            PitWindowRecommendation object
        """
        # Get tire wear info
        twi = self.fe.calculate_tire_wear_index(driver_id, current_lap)
        
        # Get driver data
        driver_laps = self.fe.lap_data[self.fe.lap_data['driver_id'] == driver_id]
        if len(driver_laps) == 0:
            raise ValueError(f"No data for driver {driver_id}")
        
        latest_lap = driver_laps.iloc[-1]
        current_tire_age = latest_lap.get('tire_age', 0)
        current_compound = latest_lap.get('tire_compound', 'Medium')
        
        # Calculate optimal pit lap
        optimal_pit_lap = twi.optimal_pit_lap or current_lap + 5
        
        # Ensure pit window is within race bounds
        optimal_pit_lap = max(current_lap + 1, min(optimal_pit_lap, total_laps - 5))
        
        # Define pit window (optimal ± 2 laps)
        pit_window_start = max(current_lap + 1, optimal_pit_lap - 2)
        pit_window_end = min(total_laps - 5, optimal_pit_lap + 2)
        
        # Determine urgency
        if twi.current_twi > 80:
            urgency = "critical"
        elif twi.current_twi > 70:
            urgency = "high"
        elif twi.current_twi > 60:
            urgency = "medium"
        else:
            urgency = "low"
        
        # Reason for pit
        if twi.current_twi > 75:
            reason = f"High tire wear (TWI: {twi.current_twi:.1f})"
        elif current_tire_age > 25:
            reason = f"High tire age ({current_tire_age} laps)"
        else:
            reason = "Strategic pit window"
        
        # Estimate time loss if pitting outside window
        # Pitting too early = lost tire life
        # Pitting too late = slower pace on worn tires
        if current_lap < pit_window_start:
            time_loss = (pit_window_start - current_lap) * 0.3  # ~0.3s per lap early
        elif current_lap > pit_window_end:
            time_loss = (current_lap - pit_window_end) * 0.5  # ~0.5s per lap late
        else:
            time_loss = 0.0
        
        # Recommend tire compound (opposite of current if high wear)
        compounds = ['Soft', 'Medium', 'Hard']
        if current_compound == 'Soft':
            recommended_compound = 'Medium' if twi.current_twi < 60 else 'Hard'
        elif current_compound == 'Medium':
            recommended_compound = 'Hard' if twi.current_twi > 50 else 'Soft'
        else:
            recommended_compound = 'Medium'
        
        return PitWindowRecommendation(
            driver_id=driver_id,
            optimal_pit_lap=optimal_pit_lap,
            pit_window_start=pit_window_start,
            pit_window_end=pit_window_end,
            urgency=urgency,
            reason=reason,
            estimated_time_loss=round(time_loss, 2),
            tire_compound_recommendation=recommended_compound
        )
    
    # ========================================================================
    # Undercut/Overcut Simulation
    # ========================================================================
    
    def simulate_undercut(
        self,
        driver_id: str,
        target_driver_id: str,
        current_lap: int,
        total_laps: int
    ) -> UndercutSimulation:
        """
        Simulate undercut/overcut opportunity
        
        Args:
            driver_id: Our driver
            target_driver_id: Driver to overtake
            current_lap: Current lap number
            total_laps: Total race laps
            
        Returns:
            UndercutSimulation object
        """
        # Get both drivers' data
        our_driver = self.fe.lap_data[self.fe.lap_data['driver_id'] == driver_id]
        target_driver = self.fe.lap_data[self.fe.lap_data['driver_id'] == target_driver_id]
        
        if len(our_driver) == 0 or len(target_driver) == 0:
            raise ValueError("Driver data not found")
        
        our_latest = our_driver.iloc[-1]
        target_latest = target_driver.iloc[-1]
        
        our_position = our_latest.get('position', 1)
        target_position = target_latest.get('position', 1)
        
        # Check if undercut is possible (we're behind)
        if our_position >= target_position:
            strategy_type = "undercut"  # Pit early to get ahead
        else:
            strategy_type = "overcut"  # Stay out longer
        
        # Get pace comparison
        our_pace = our_driver['lap_time'].tail(5).mean()
        target_pace = target_driver['lap_time'].tail(5).mean()
        pace_delta = our_pace - target_pace
        
        # Calculate optimal pit lap for undercut
        # Pit 1-2 laps before target to gain track position
        if strategy_type == "undercut":
            target_twi = self.fe.calculate_tire_wear_index(target_driver_id, current_lap)
            optimal_pit_lap = max(current_lap + 1, (target_twi.optimal_pit_lap or current_lap + 10) - 2)
        else:  # overcut
            our_twi = self.fe.calculate_tire_wear_index(driver_id, current_lap)
            optimal_pit_lap = min(total_laps - 5, (our_twi.optimal_pit_lap or current_lap + 10) + 2)
        
        # Estimate expected gain
        # Undercut: gain from fresh tires while target on old tires
        # Overcut: gain from staying out while target pits
        if strategy_type == "undercut":
            # Fresh tires vs old tires advantage
            tire_advantage = 1.5  # ~1.5s advantage with fresh tires
            expected_gain = max(0, tire_advantage - abs(pace_delta))
        else:
            # Track position gain while target pits
            expected_gain = max(0, 2.0 - abs(pace_delta))  # ~2s from track position
        
        # Success probability
        # Based on pace difference and tire condition
        if abs(pace_delta) < 0.5:  # Similar pace
            success_prob = 0.7
        elif (strategy_type == "undercut" and pace_delta < 0):  # We're faster
            success_prob = 0.8
        elif (strategy_type == "overcut" and pace_delta > 0):  # We're slower but can overcut
            success_prob = 0.6
        else:
            success_prob = 0.4
        
        # Risk factors
        risk_factors = []
        if abs(pace_delta) > 1.0:
            risk_factors.append("Large pace difference")
        if optimal_pit_lap < current_lap + 3:
            risk_factors.append("Very early pit stop")
        if optimal_pit_lap > total_laps - 5:
            risk_factors.append("Very late pit stop")
        
        return UndercutSimulation(
            driver_id=driver_id,
            target_driver_id=target_driver_id,
            strategy_type=strategy_type,
            optimal_pit_lap=optimal_pit_lap,
            expected_gain=round(expected_gain, 2),
            success_probability=round(success_prob, 2),
            risk_factors=risk_factors
        )
    
    # ========================================================================
    # Pace Projection
    # ========================================================================
    
    def project_pace(
        self,
        driver_id: str,
        current_lap: int,
        projection_laps: int = 10
    ) -> PaceProjection:
        """
        Project future lap pace
        
        Args:
            driver_id: Driver identifier
            current_lap: Current lap number
            projection_laps: Number of laps to project ahead
            
        Returns:
            PaceProjection object
        """
        driver_laps = self.fe.lap_data[self.fe.lap_data['driver_id'] == driver_id]
        
        if len(driver_laps) == 0:
            raise ValueError(f"No data for driver {driver_id}")
        
        # Get current metrics
        twi = self.fe.calculate_tire_wear_index(driver_id, current_lap)
        pace_delta = self.fe.calculate_pace_delta_trend(driver_id)
        track_evolution = self.fe.calculate_track_evolution()
        
        latest_lap = driver_laps.iloc[-1]
        current_pace = latest_lap['lap_time']
        current_tire_age = latest_lap.get('tire_age', 0)
        
        # Project pace for next N laps
        projected_laps = []
        
        for i in range(1, projection_laps + 1):
            future_lap = current_lap + i
            future_tire_age = current_tire_age + i
            
            # Tire degradation effect
            degradation_per_lap = twi.degradation_rate / 10  # Convert to seconds
            tire_effect = degradation_per_lap * i
            
            # Track evolution effect (negative = faster)
            track_effect = track_evolution.evolution_rate * i
            
            # Fuel effect (lighter = faster, but minimal)
            fuel_effect = -0.02 * i  # 0.02s per lap lighter
            
            # Projected pace
            projected_pace = current_pace + tire_effect - track_effect - fuel_effect
            
            projected_laps.append({
                "lap": future_lap,
                "pace": round(projected_pace, 3)
            })
        
        # Factors considered
        factors = [
            f"Tire degradation ({twi.degradation_rate:.2f} TWI/lap)",
            f"Track evolution ({track_evolution.evolution_rate:.4f} s/lap)",
            "Fuel load reduction",
            f"Current TWI: {twi.current_twi:.1f}"
        ]
        
        # Confidence based on data quality
        confidence = min(1.0, len(driver_laps) / 20)  # More data = higher confidence
        
        return PaceProjection(
            driver_id=driver_id,
            current_lap=current_lap,
            projected_laps=projected_laps,
            factors_considered=factors,
            confidence=round(confidence, 2)
        )

