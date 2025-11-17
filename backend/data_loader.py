"""
Data loading utilities for GR Race Strategist AI
Handles loading and parsing of TRD hackathon datasets
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict
from pathlib import Path
import json
from models import LapData, DriverData, RaceState


class RaceDataLoader:
    """
    Loads and processes racing data from various formats
    Supports CSV, JSON, and pandas DataFrames
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize data loader
        
        Args:
            data_path: Path to data directory or file
        """
        self.data_path = Path(data_path) if data_path else None
        self.lap_data: Optional[pd.DataFrame] = None
        self.driver_data: Optional[pd.DataFrame] = None
    
    def load_from_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load data from CSV file
        
        Expected columns (flexible - will map common variations):
        - lap_number, lap, lapNumber
        - driver_id, driverId, driver
        - lap_time, lapTime, time
        - tire_compound, tireCompound, compound
        - tire_age, tireAge, laps_on_tires
        - position, pos
        - sector_1_time, sector1, s1
        - sector_2_time, sector2, s2
        - sector_3_time, sector3, s3
        """
        df = pd.read_csv(file_path)
        
        # Normalize column names (handle common variations)
        column_mapping = {
            'lap': 'lap_number',
            'lapNumber': 'lap_number',
            'driverId': 'driver_id',
            'driver': 'driver_id',
            'lapTime': 'lap_time',
            'time': 'lap_time',
            'tireCompound': 'tire_compound',
            'compound': 'tire_compound',
            'tireAge': 'tire_age',
            'laps_on_tires': 'tire_age',
            'pos': 'position',
            'sector1': 'sector_1_time',
            's1': 'sector_1_time',
            'sector2': 'sector_2_time',
            's2': 'sector_2_time',
            'sector3': 'sector_3_time',
            's3': 'sector_3_time',
        }
        
        df = df.rename(columns=column_mapping)
        
        # Ensure required columns exist
        required_cols = ['lap_number', 'driver_id', 'lap_time']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        self.lap_data = df
        return df
    
    def load_from_json(self, file_path: str) -> pd.DataFrame:
        """Load data from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Handle both list of dicts and nested structures
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict) and 'laps' in data:
            df = pd.DataFrame(data['laps'])
        else:
            raise ValueError("JSON format not recognized")
        
        self.lap_data = df
        return df
    
    def load_from_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Use existing pandas DataFrame"""
        self.lap_data = df
        return df
    
    def validate_data(self) -> Dict[str, bool]:
        """
        Validate loaded data for common issues
        
        Returns:
            Dictionary with validation results
        """
        if self.lap_data is None:
            return {"loaded": False, "error": "No data loaded"}
        
        results = {
            "loaded": True,
            "total_laps": len(self.lap_data),
            "unique_drivers": self.lap_data['driver_id'].nunique() if 'driver_id' in self.lap_data.columns else 0,
            "missing_lap_times": self.lap_data['lap_time'].isna().sum(),
            "negative_lap_times": (self.lap_data['lap_time'] < 0).sum() if 'lap_time' in self.lap_data.columns else 0,
            "duplicate_laps": self.lap_data.duplicated(subset=['lap_number', 'driver_id']).sum(),
        }
        
        return results
    
    def get_lap_data_objects(self, limit: Optional[int] = None) -> List[LapData]:
        """
        Convert DataFrame to list of LapData objects
        
        Args:
            limit: Optional limit on number of records
            
        Returns:
            List of LapData objects
        """
        if self.lap_data is None:
            raise ValueError("No data loaded. Call load_from_csv() or load_from_dataframe() first.")
        
        df = self.lap_data.head(limit) if limit else self.lap_data
        
        lap_objects = []
        for _, row in df.iterrows():
            lap_obj = LapData(
                lap_number=int(row['lap_number']),
                driver_id=str(row['driver_id']),
                lap_time=float(row['lap_time']),
                sector_1_time=float(row['sector_1_time']) if pd.notna(row.get('sector_1_time')) else None,
                sector_2_time=float(row['sector_2_time']) if pd.notna(row.get('sector_2_time')) else None,
                sector_3_time=float(row['sector_3_time']) if pd.notna(row.get('sector_3_time')) else None,
                tire_compound=str(row['tire_compound']) if pd.notna(row.get('tire_compound')) else "Medium",
                tire_age=int(row['tire_age']) if pd.notna(row.get('tire_age')) else 0,
                fuel_load=float(row['fuel_load']) if pd.notna(row.get('fuel_load')) else None,
                position=int(row['position']) if pd.notna(row.get('position')) else 1,
                track_temperature=float(row['track_temperature']) if pd.notna(row.get('track_temperature')) else None,
                air_temperature=float(row['air_temperature']) if pd.notna(row.get('air_temperature')) else None,
            )
            lap_objects.append(lap_obj)
        
        return lap_objects
    
    def get_driver_summary(self) -> List[DriverData]:
        """
        Generate driver summary statistics from lap data
        
        Returns:
            List of DriverData objects
        """
        if self.lap_data is None:
            raise ValueError("No data loaded")
        
        driver_summaries = []
        
        for driver_id in self.lap_data['driver_id'].unique():
            driver_laps = self.lap_data[self.lap_data['driver_id'] == driver_id]
            
            # Get latest position and tire info
            latest_lap = driver_laps.iloc[-1]
            
            driver_summary = DriverData(
                driver_id=str(driver_id),
                driver_name=None,
                current_position=int(latest_lap['position']) if pd.notna(latest_lap.get('position')) else 1,
                current_tire_compound=str(latest_lap['tire_compound']) if pd.notna(latest_lap.get('tire_compound')) else "Medium",
                current_tire_age=int(latest_lap['tire_age']) if pd.notna(latest_lap.get('tire_age')) else 0,
                total_laps=len(driver_laps),
                best_lap_time=float(driver_laps['lap_time'].min()),
                average_lap_time=float(driver_laps['lap_time'].mean()),
            )
            
            driver_summaries.append(driver_summary)
        
        return driver_summaries


# REMOVED: create_sample_data() function
# This application ONLY uses real-time TRD hackathon data from Data-GR folder
# No mock, sample, or AI-generated data is allowed

