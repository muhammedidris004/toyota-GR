"""
Telemetry-based Feature Engineering
Uses telemetry data to enhance racing features
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from pathlib import Path


class TelemetryFeatureEngineer:
    """
    Extract advanced features from telemetry data
    """
    
    def __init__(self, telemetry_path: Optional[str] = None):
        """
        Initialize telemetry feature engineer
        
        Args:
            telemetry_path: Path to telemetry CSV file
        """
        self.telemetry_path = Path(telemetry_path) if telemetry_path else None
        self.telemetry_data: Optional[pd.DataFrame] = None
    
    def load_telemetry(self, file_path: str) -> pd.DataFrame:
        """
        Load telemetry data from CSV
        
        Note: Telemetry files can be very large (>200MB)
        We'll sample or aggregate for performance
        """
        # For large files, we'll read in chunks or sample
        try:
            # Try to read first 100k rows as sample
            df = pd.read_csv(file_path, nrows=100000)
            self.telemetry_data = df
            return df
        except Exception as e:
            print(f"Warning: Could not load full telemetry file: {e}")
            return pd.DataFrame()
    
    def calculate_driving_intensity(self, driver_id: str, lap_number: int) -> Dict[str, float]:
        """
        Calculate driving intensity metrics from telemetry
        
        Returns:
            Dictionary with intensity metrics
        """
        if self.telemetry_data is None or len(self.telemetry_data) == 0:
            return {
                'avg_throttle': 0.0,
                'avg_brake_pressure': 0.0,
                'max_lateral_g': 0.0,
                'avg_speed': 0.0,
                'intensity_score': 0.0
            }
        
        # Filter for driver and lap (if vehicle_id column exists)
        driver_data = self.telemetry_data.copy()
        
        # Calculate basic metrics
        metrics = {
            'avg_throttle': 0.0,
            'avg_brake_pressure': 0.0,
            'max_lateral_g': 0.0,
            'avg_speed': 0.0,
            'intensity_score': 0.0
        }
        
        # If we have throttle data
        if 'ath' in driver_data.columns or 'aps' in driver_data.columns:
            throttle_col = 'ath' if 'ath' in driver_data.columns else 'aps'
            metrics['avg_throttle'] = float(driver_data[throttle_col].mean()) if len(driver_data) > 0 else 0.0
        
        # If we have brake data
        if 'pbrake_f' in driver_data.columns:
            metrics['avg_brake_pressure'] = float(driver_data['pbrake_f'].mean()) if len(driver_data) > 0 else 0.0
        
        # If we have lateral acceleration
        if 'accy_can' in driver_data.columns:
            metrics['max_lateral_g'] = float(driver_data['accy_can'].abs().max()) if len(driver_data) > 0 else 0.0
        
        # If we have speed data
        if 'Speed' in driver_data.columns:
            metrics['avg_speed'] = float(driver_data['Speed'].mean()) if len(driver_data) > 0 else 0.0
        
        # Calculate intensity score (0-100)
        # Higher throttle, brake, lateral G = higher intensity
        intensity = (
            (metrics['avg_throttle'] / 100.0) * 0.3 +
            (min(metrics['avg_brake_pressure'] / 50.0, 1.0)) * 0.3 +
            (min(metrics['max_lateral_g'] / 2.0, 1.0)) * 0.2 +
            (min(metrics['avg_speed'] / 200.0, 1.0)) * 0.2
        ) * 100
        
        metrics['intensity_score'] = min(100, max(0, intensity))
        
        return metrics
    
    def calculate_tire_stress(self, driver_id: str, lap_number: int) -> Dict[str, float]:
        """
        Calculate tire stress from telemetry
        
        Based on:
        - Lateral forces (cornering)
        - Braking forces
        - Acceleration forces
        """
        if self.telemetry_data is None or len(self.telemetry_data) == 0:
            return {
                'lateral_stress': 0.0,
                'braking_stress': 0.0,
                'acceleration_stress': 0.0,
                'total_stress': 0.0
            }
        
        driver_data = self.telemetry_data.copy()
        
        stress = {
            'lateral_stress': 0.0,
            'braking_stress': 0.0,
            'acceleration_stress': 0.0,
            'total_stress': 0.0
        }
        
        # Lateral stress from cornering
        if 'accy_can' in driver_data.columns:
            stress['lateral_stress'] = float(driver_data['accy_can'].abs().mean()) * 50
        
        # Braking stress
        if 'pbrake_f' in driver_data.columns:
            stress['braking_stress'] = float(driver_data['pbrake_f'].mean()) * 2
        
        # Acceleration stress
        if 'accx_can' in driver_data.columns:
            accel_data = driver_data[driver_data['accx_can'] > 0]
            if len(accel_data) > 0:
                stress['acceleration_stress'] = float(accel_data['accx_can'].mean()) * 30
        
        # Total stress (normalized 0-100)
        stress['total_stress'] = min(100, (
            stress['lateral_stress'] * 0.4 +
            stress['braking_stress'] * 0.4 +
            stress['acceleration_stress'] * 0.2
        ))
        
        return stress
    
    def calculate_fuel_consumption_rate(self, driver_id: str) -> float:
        """
        Estimate fuel consumption rate from telemetry
        
        Based on throttle usage and speed
        """
        if self.telemetry_data is None or len(self.telemetry_data) == 0:
            return 2.5  # Default: 2.5 kg per lap
        
        driver_data = self.telemetry_data.copy()
        
        # Estimate based on throttle usage
        if 'ath' in driver_data.columns or 'aps' in driver_data.columns:
            throttle_col = 'ath' if 'ath' in driver_data.columns else 'aps'
            avg_throttle = driver_data[throttle_col].mean()
            
            # Higher throttle = more fuel consumption
            # Base: 2.0 kg/lap, up to 3.5 kg/lap at full throttle
            fuel_rate = 2.0 + (avg_throttle / 100.0) * 1.5
            return float(fuel_rate)
        
        return 2.5  # Default


def enhance_tire_wear_with_telemetry(
    base_twi: float,
    telemetry_stress: Dict[str, float],
    degradation_rate: float
) -> float:
    """
    Enhance tire wear calculation with telemetry stress data
    
    Args:
        base_twi: Base tire wear index
        telemetry_stress: Stress metrics from telemetry
        degradation_rate: Base degradation rate
        
    Returns:
        Enhanced TWI
    """
    stress_factor = telemetry_stress.get('total_stress', 50) / 100.0
    
    # Higher stress = faster degradation
    # Stress factor: 0.8 (low stress) to 1.3 (high stress)
    stress_multiplier = 0.8 + (stress_factor * 0.5)
    
    enhanced_twi = base_twi * stress_multiplier
    return min(100, enhanced_twi)


def enhance_pace_projection_with_telemetry(
    base_pace: float,
    telemetry_intensity: Dict[str, float],
    current_lap: int
) -> float:
    """
    Enhance pace projection with telemetry intensity data
    
    Args:
        base_pace: Base projected pace
        telemetry_intensity: Intensity metrics from telemetry
        current_lap: Current lap number
        
    Returns:
        Enhanced pace projection
    """
    intensity = telemetry_intensity.get('intensity_score', 50) / 100.0
    
    # Higher intensity = potentially faster pace (if driver is pushing)
    # But also higher tire wear
    # Balance: intensity helps pace but hurts tire wear
    
    # Intensity factor: 0.95 (low) to 1.05 (high) for pace
    # But also increases degradation
    intensity_pace_factor = 0.95 + (intensity * 0.1)
    
    enhanced_pace = base_pace / intensity_pace_factor
    return enhanced_pace

