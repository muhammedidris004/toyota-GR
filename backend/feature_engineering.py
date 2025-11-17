"""
Feature Engineering Module for GR Race Strategist AI
Calculates racing-specific features from lap data
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from models import (
    TireWearIndex, DriverConsistencyScore, TrafficLossFactor,
    TrackEvolutionRate, PaceDeltaTrend
)


class FeatureEngineer:
    """
    Engine for calculating racing features:
    - Tire Wear Index (TWI)
    - Driver Consistency Score
    - Traffic Loss Factor
    - Track Evolution Rate
    - Pace Delta Trends
    """
    
    def __init__(self, lap_data: pd.DataFrame):
        """
        Initialize feature engineer with lap data
        
        Args:
            lap_data: DataFrame with lap data (from data_loader)
        """
        self.lap_data = lap_data.copy()
        self._preprocess_data()
    
    def _preprocess_data(self):
        """Preprocess data for feature engineering"""
        # Sort by driver and lap number
        self.lap_data = self.lap_data.sort_values(['driver_id', 'lap_number'])
        
        # Calculate rolling averages
        self.lap_data['rolling_avg_5'] = (
            self.lap_data.groupby('driver_id')['lap_time']
            .rolling(window=5, min_periods=1)
            .mean()
            .reset_index(0, drop=True)
        )
    
    # ========================================================================
    # Tire Wear Index (TWI)
    # ========================================================================
    
    def calculate_tire_wear_index(
        self,
        driver_id: str,
        current_lap: Optional[int] = None
    ) -> TireWearIndex:
        """
        Calculate Tire Wear Index (TWI) for a driver
        
        TWI Formula:
        - Base degradation based on tire compound and age
        - Adjusted for track temperature and driving style
        - 0 = new tires, 100 = completely worn
        
        Args:
            driver_id: Driver identifier
            current_lap: Current lap number (uses latest if None)
            
        Returns:
            TireWearIndex object
        """
        driver_laps = self.lap_data[self.lap_data['driver_id'] == driver_id].copy()
        
        if len(driver_laps) == 0:
            raise ValueError(f"No data found for driver {driver_id}")
        
        if current_lap:
            driver_laps = driver_laps[driver_laps['lap_number'] <= current_lap]
        
        latest_lap = driver_laps.iloc[-1]
        
        # Get tire compound and age
        tire_compound = latest_lap.get('tire_compound', 'Medium')
        tire_age = latest_lap.get('tire_age', 0)
        
        # Base degradation rates per compound (per lap)
        degradation_rates = {
            'Soft': 2.5,    # Fastest degradation
            'Medium': 1.5,
            'Hard': 1.0     # Slowest degradation
        }
        
        base_degradation = degradation_rates.get(tire_compound, 1.5)
        
        # Try to use adaptive degradation if available (from ML models)
        # This will be enhanced when ML models are initialized
        try:
            # Check if we can calculate adaptive rate from data
            if len(driver_laps) >= 5:
                recent_laps = driver_laps.tail(min(10, len(driver_laps)))
                if len(recent_laps) >= 3:
                    # Calculate actual degradation from pace change
                    lap_times = recent_laps['lap_time'].values
                    x = np.arange(len(lap_times))
                    if len(lap_times) > 1 and np.std(lap_times) > 0:
                        slope = np.polyfit(x, lap_times, 1)[0]
                        # Convert pace degradation to TWI (0.1s = 1 TWI)
                        adaptive_rate = abs(slope) * 10
                        # Blend: 60% adaptive, 40% base
                        base_degradation = 0.6 * adaptive_rate + 0.4 * base_degradation
        except:
            pass  # Fall back to base degradation
        
        # Calculate current TWI (0-100 scale)
        # Exponential degradation model
        current_twi = min(100, base_degradation * tire_age * (1 + tire_age * 0.02))
        
        # Calculate degradation rate (TWI increase per lap)
        degradation_rate = base_degradation * (1 + tire_age * 0.02)
        
        # Project TWI for next 10 laps
        projected_twi = min(100, current_twi + (degradation_rate * 10))
        
        # Find optimal pit lap (when TWI > 70 or pace drops significantly)
        optimal_pit_lap = None
        if current_twi > 70:
            optimal_pit_lap = latest_lap['lap_number']
        else:
            # Project when TWI will hit 70
            laps_to_70 = max(0, (70 - current_twi) / degradation_rate)
            optimal_pit_lap = int(latest_lap['lap_number'] + laps_to_70)
        
        return TireWearIndex(
            driver_id=driver_id,
            current_twi=round(current_twi, 2),
            projected_twi=round(projected_twi, 2),
            degradation_rate=round(degradation_rate, 2),
            optimal_pit_lap=optimal_pit_lap
        )
    
    # ========================================================================
    # Driver Consistency Score
    # ========================================================================
    
    def calculate_consistency_score(
        self,
        driver_id: str,
        window: int = 10
    ) -> DriverConsistencyScore:
        """
        Calculate driver consistency score
        
        Consistency Score Formula:
        - Based on lap time variance
        - Lower variance = higher consistency
        - Normalized to 0-100 scale
        
        Args:
            driver_id: Driver identifier
            window: Number of recent laps to consider
            
        Returns:
            DriverConsistencyScore object
        """
        driver_laps = self.lap_data[self.lap_data['driver_id'] == driver_id].copy()
        
        if len(driver_laps) == 0:
            raise ValueError(f"No data found for driver {driver_id}")
        
        # Get recent laps
        recent_laps = driver_laps.tail(window)
        
        # Calculate variance
        lap_times = recent_laps['lap_time'].values
        variance = np.var(lap_times)
        std_dev = np.std(lap_times)
        mean_lap_time = np.mean(lap_times)
        
        # Consistency score: inverse of coefficient of variation
        # Higher score = more consistent
        cv = std_dev / mean_lap_time if mean_lap_time > 0 else 1.0
        consistency_score = max(0, min(100, 100 * (1 - cv * 5)))  # Normalize to 0-100
        
        # Sector variances
        sector_variance = {}
        for sector in ['sector_1_time', 'sector_2_time', 'sector_3_time']:
            if sector in recent_laps.columns:
                sector_times = recent_laps[sector].dropna()
                if len(sector_times) > 0:
                    sector_variance[sector] = round(float(np.var(sector_times)), 3)
        
        # Determine trend (improving, stable, degrading)
        if len(lap_times) >= 3:
            recent_avg = np.mean(lap_times[-3:])
            earlier_avg = np.mean(lap_times[-6:-3]) if len(lap_times) >= 6 else recent_avg
            
            if recent_avg < earlier_avg - 0.1:
                trend = "improving"
            elif recent_avg > earlier_avg + 0.1:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return DriverConsistencyScore(
            driver_id=driver_id,
            consistency_score=round(consistency_score, 2),
            lap_time_variance=round(variance, 3),
            sector_variance=sector_variance,
            recent_trend=trend
        )
    
    # ========================================================================
    # Traffic Loss Factor
    # ========================================================================
    
    def calculate_traffic_loss(
        self,
        driver_id: str,
        current_lap: Optional[int] = None
    ) -> TrafficLossFactor:
        """
        Calculate traffic impact on lap time
        
        Traffic Loss Formula:
        - Compare pace when in clean air vs. following cars
        - Account for dirty air effect
        - Estimate overtake opportunities
        
        Args:
            driver_id: Driver identifier
            current_lap: Current lap number
            
        Returns:
            TrafficLossFactor object
        """
        driver_laps = self.lap_data[self.lap_data['driver_id'] == driver_id].copy()
        
        if len(driver_laps) == 0:
            raise ValueError(f"No data found for driver {driver_id}")
        
        if current_lap:
            driver_laps = driver_laps[driver_laps['lap_number'] <= current_lap]
        
        latest_lap = driver_laps.iloc[-1]
        current_position = latest_lap.get('position', 1)
        
        # Estimate cars ahead (simplified - in real data, use actual gaps)
        total_drivers = self.lap_data['driver_id'].nunique()
        cars_ahead = max(0, current_position - 1)
        
        # Calculate baseline pace (best clean air lap)
        baseline_pace = driver_laps['lap_time'].min()
        current_pace = latest_lap['lap_time']
        
        # Traffic loss = difference from baseline (simplified model)
        # In reality, would compare clean air vs dirty air laps
        traffic_loss = max(0, current_pace - baseline_pace) * 0.3  # 30% attributed to traffic
        
        # Dirty air factor (0-1, higher = more impact)
        # More cars ahead = more dirty air
        dirty_air_factor = min(1.0, cars_ahead / max(1, total_drivers - 1))
        
        # Overtake opportunity (simplified)
        # If pace is significantly faster than cars ahead, opportunity exists
        overtake_opportunity = (
            cars_ahead > 0 and
            current_pace < baseline_pace + 0.5  # Within 0.5s of best pace
        )
        
        return TrafficLossFactor(
            driver_id=driver_id,
            traffic_loss=round(traffic_loss, 3),
            cars_ahead=cars_ahead,
            dirty_air_factor=round(dirty_air_factor, 2),
            overtake_opportunity=overtake_opportunity
        )
    
    # ========================================================================
    # Track Evolution Rate
    # ========================================================================
    
    def calculate_track_evolution(
        self,
        window: int = 20
    ) -> TrackEvolutionRate:
        """
        Calculate track evolution (grip improvement over time)
        
        Track Evolution Formula:
        - Track gets faster as rubber is laid down
        - Measure average lap time improvement over race
        - Project optimal grip level
        
        Args:
            window: Number of recent laps to analyze
            
        Returns:
            TrackEvolutionRate object
        """
        # Get all drivers' recent laps
        recent_laps = self.lap_data.tail(window * self.lap_data['driver_id'].nunique())
        
        # Group by lap number and calculate average pace
        avg_pace_by_lap = recent_laps.groupby('lap_number')['lap_time'].mean().sort_index()
        
        if len(avg_pace_by_lap) < 2:
            # Not enough data
            return TrackEvolutionRate(
                evolution_rate=0.0,
                track_grip_level=50.0,
                rubber_laying_effect=0.0,
                projected_optimal_lap=None
            )
        
        # Calculate evolution rate (negative = getting faster)
        early_laps = avg_pace_by_lap.head(5).mean()
        late_laps = avg_pace_by_lap.tail(5).mean()
        lap_span = len(avg_pace_by_lap) - 1
        
        if lap_span > 0:
            evolution_rate = (late_laps - early_laps) / lap_span  # Negative = faster
        else:
            evolution_rate = 0.0
        
        # Track grip level (0-100, higher = more grip)
        # Based on how much faster track has gotten
        max_improvement = 2.0  # Assume max 2s improvement possible
        improvement = max(0, early_laps - late_laps)
        track_grip_level = min(100, 50 + (improvement / max_improvement) * 50)
        
        # Rubber laying effect (cumulative)
        rubber_laying_effect = max(0, improvement)
        
        # Project optimal lap (when track is fully rubbered in)
        # Simplified: assume optimal at 80% grip level
        if evolution_rate < -0.01:  # Track still improving
            laps_to_optimal = (80 - track_grip_level) / abs(evolution_rate * 10)
            projected_optimal_lap = int(avg_pace_by_lap.index[-1] + laps_to_optimal)
        else:
            projected_optimal_lap = None
        
        return TrackEvolutionRate(
            evolution_rate=round(evolution_rate, 4),
            track_grip_level=round(track_grip_level, 2),
            rubber_laying_effect=round(rubber_laying_effect, 3),
            projected_optimal_lap=projected_optimal_lap
        )
    
    # ========================================================================
    # Pace Delta Trends
    # ========================================================================
    
    def calculate_pace_delta_trend(
        self,
        driver_id: str,
        reference_pace: Optional[float] = None,
        window: int = 10
    ) -> PaceDeltaTrend:
        """
        Calculate pace delta trends
        
        Pace Delta Formula:
        - Compare driver's pace to reference (fastest driver or baseline)
        - Track trend over recent laps
        - Project future pace
        
        Args:
            driver_id: Driver identifier
            reference_pace: Reference pace (uses fastest if None)
            window: Number of recent laps to analyze
            
        Returns:
            PaceDeltaTrend object
        """
        driver_laps = self.lap_data[self.lap_data['driver_id'] == driver_id].copy()
        
        if len(driver_laps) == 0:
            raise ValueError(f"No data found for driver {driver_id}")
        
        recent_laps = driver_laps.tail(window)
        
        # Get reference pace (fastest driver's average or provided)
        if reference_pace is None:
            all_drivers_avg = self.lap_data.groupby('driver_id')['lap_time'].mean()
            reference_pace = all_drivers_avg.min()
        
        # Calculate pace deltas
        pace_deltas = (recent_laps['lap_time'] - reference_pace).tolist()
        current_pace_delta = pace_deltas[-1] if pace_deltas else 0.0
        
        # Determine trend direction
        if len(pace_deltas) >= 3:
            recent_avg = np.mean(pace_deltas[-3:])
            earlier_avg = np.mean(pace_deltas[-6:-3]) if len(pace_deltas) >= 6 else recent_avg
            
            if recent_avg < earlier_avg - 0.1:
                trend = "improving"
            elif recent_avg > earlier_avg + 0.1:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Project future pace (simple linear projection)
        if len(pace_deltas) >= 2:
            trend_slope = (pace_deltas[-1] - pace_deltas[0]) / len(pace_deltas)
            projected_pace = current_pace_delta + (trend_slope * 5)  # Project 5 laps ahead
        else:
            projected_pace = current_pace_delta
        
        return PaceDeltaTrend(
            driver_id=driver_id,
            current_pace_delta=round(current_pace_delta, 3),
            pace_trend=[round(d, 3) for d in pace_deltas],
            trend_direction=trend,
            projected_pace=round(projected_pace, 3)
        )

