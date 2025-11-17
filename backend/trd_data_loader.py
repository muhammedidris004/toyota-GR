"""
TRD Hackathon Data Loader
Specialized loader for Toyota GR Cup racing data format
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List
import re
from data_loader import RaceDataLoader


class TRDDataLoader:
    """
    Loader for TRD hackathon dataset format
    Handles Analysis files, lap_time files, and Results files
    """
    
    def __init__(self, data_root: str = "Data-GR"):
        """
        Initialize TRD data loader
        
        Args:
            data_root: Root directory of Data-GR folder (default: Data-GR, located in backend/)
        """
        self.data_root = Path(data_root)
        self.race_data: Optional[pd.DataFrame] = None
    
    def load_analysis_file(
        self,
        track: str,
        race: str = "Race 1",
        file_pattern: str = "23_AnalysisEnduranceWithSections"
    ) -> pd.DataFrame:
        """
        Load analysis file with lap data
        
        Args:
            track: Track name (e.g., "COTA", "Sonoma", "barber")
            race: Race number ("Race 1" or "Race 2") or None for single-race tracks
            file_pattern: File name pattern to match
            
        Returns:
            DataFrame with normalized lap data
        """
        track_path = self.data_root / track
        
        # Try multiple structures:
        # 1. Track/Race 1/ or Track/Race 2/ (COTA, Sonoma style)
        # 2. Track/*Race 1* or Track/*Race 2* (barber, indianapolis style)
        # 3. Track/Subfolder/Race 1/ (road-america/Road America, sebring/Sebring, etc.)
        
        analysis_files = []
        
        # First, try direct subdirectory structure (COTA, Sonoma)
        race_path = track_path / race
        if race_path.exists() and race_path.is_dir():
            analysis_files = list(race_path.glob(f"*{file_pattern}*"))
        
        # If not found, check for nested subdirectory (road-america/Road America/Race 1/)
        if not analysis_files:
            for subdir in track_path.iterdir():
                if subdir.is_dir() and not subdir.name.startswith('.'):
                    nested_race_path = subdir / race
                    if nested_race_path.exists() and nested_race_path.is_dir():
                        analysis_files = list(nested_race_path.glob(f"*{file_pattern}*"))
                        if analysis_files:
                            break
        
        # If not found, try root-level files with race in filename (barber, indianapolis)
        if not analysis_files:
            # Look for files with race number in the name
            race_num = race.replace("Race ", "Race_").replace("Race ", "_Race_")
            analysis_files = list(track_path.glob(f"*{file_pattern}*{race_num}*"))
            # Also try without underscore
            if not analysis_files:
                analysis_files = list(track_path.glob(f"*{file_pattern}*{race}*"))
            
            # Also check in subdirectories
            if not analysis_files:
                for subdir in track_path.iterdir():
                    if subdir.is_dir():
                        race_num = race.replace("Race ", "Race_")
                        analysis_files = list(subdir.glob(f"*{file_pattern}*{race_num}*"))
                        if not analysis_files:
                            analysis_files = list(subdir.glob(f"*{file_pattern}*{race}*"))
                        if analysis_files:
                            break
        
        # If still not found, try any analysis file (for single-race tracks)
        if not analysis_files:
            # Check root level
            analysis_files = list(track_path.glob(f"*{file_pattern}*"))
            # Check subdirectories
            if not analysis_files:
                for subdir in track_path.iterdir():
                    if subdir.is_dir():
                        analysis_files = list(subdir.glob(f"*{file_pattern}*"))
                        if analysis_files:
                            break
            
            # Filter out files that explicitly mention other races
            if len(analysis_files) > 1:
                # Remove files that mention "Race 2" if we want "Race 1"
                if "Race 1" in race or "Race_1" in race:
                    analysis_files = [f for f in analysis_files if "Race 2" not in f.name and "Race_2" not in f.name]
                elif "Race 2" in race or "Race_2" in race:
                    analysis_files = [f for f in analysis_files if "Race 1" not in f.name and "Race_1" not in f.name]
        
        if not analysis_files:
            raise FileNotFoundError(
                f"No analysis file found for {track} {race}. "
                f"Checked: {track_path / race}, {track_path}/*{file_pattern}*{race}*, and subdirectories"
            )
        
        analysis_file = analysis_files[0]
        
        # Read CSV (semicolon-separated)
        df = pd.read_csv(analysis_file, sep=';', encoding='utf-8')
        
        # Normalize column names (remove spaces, handle variations)
        df.columns = df.columns.str.strip()
        
        # Map columns to our standard format
        column_mapping = {
            'LAP_NUMBER': 'lap_number',
            'lap_number': 'lap_number',
            'NUMBER': 'car_number',
            'DRIVER_NUMBER': 'driver_number',
            'LAP_TIME': 'lap_time',
            'lap_time': 'lap_time',
            'S1': 'sector_1_time',
            'S1_SECONDS': 'sector_1_time',
            'S2': 'sector_2_time',
            'S2_SECONDS': 'sector_2_time',
            'S3': 'sector_3_time',
            'S3_SECONDS': 'sector_3_time',
            'KPH': 'speed_kph',
            'TOP_SPEED': 'top_speed',
        }
        
        # Rename columns
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        # Convert lap_time to seconds if needed
        if 'lap_time' in df.columns:
            df['lap_time'] = df['lap_time'].apply(self._parse_time_to_seconds)
        
        # Convert sector times to seconds
        # Handle both S1/S1_SECONDS, S2/S2_SECONDS, etc.
        sector_mapping = {
            'S1': 'sector_1_time',
            'S1_SECONDS': 'sector_1_time',
            'S2': 'sector_2_time',
            'S2_SECONDS': 'sector_2_time',
            'S3': 'sector_3_time',
            'S3_SECONDS': 'sector_3_time',
        }
        
        # Rename sector columns first to avoid duplicates
        for old_col, new_col in sector_mapping.items():
            if old_col in df.columns and new_col not in df.columns:
                df[new_col] = df[old_col].apply(self._parse_time_to_seconds)
        
        # Convert existing sector columns if they exist
        for sector in ['sector_1_time', 'sector_2_time', 'sector_3_time']:
            if sector in df.columns:
                df[sector] = df[sector].apply(self._parse_time_to_seconds)
        
        # Create driver_id from car_number or driver_number
        if 'car_number' in df.columns:
            df['driver_id'] = df['car_number'].astype(str).apply(
                lambda x: f"DRIVER_{x.zfill(2)}"
            )
        elif 'driver_number' in df.columns:
            df['driver_id'] = df['driver_number'].astype(str).apply(
                lambda x: f"DRIVER_{x.zfill(2)}"
            )
        else:
            raise ValueError("No car_number or driver_number column found")
        
        # Ensure lap_number is integer
        if 'lap_number' in df.columns:
            df['lap_number'] = pd.to_numeric(df['lap_number'], errors='coerce').astype('Int64')
        
        # Filter out invalid laps (like 32768 mentioned in extra.md)
        if 'lap_number' in df.columns:
            df = df[df['lap_number'] < 1000]  # Remove obviously invalid lap numbers
        
        # Add track and race info
        df['track'] = track
        df['race'] = race
        
        # Sort by driver and lap
        df = df.sort_values(['driver_id', 'lap_number']).reset_index(drop=True)
        
        self.race_data = df
        return df
    
    def load_lap_time_file(
        self,
        track: str,
        race: str = "Race 1"
    ) -> pd.DataFrame:
        """
        Load lap_time CSV file (raw telemetry format)
        
        Args:
            track: Track name
            race: Race number
            
        Returns:
            DataFrame with lap times
        """
        track_path = self.data_root / track / race
        
        # Find lap_time file (various naming patterns)
        lap_time_files = list(track_path.glob("*lap_time*.csv"))
        
        if not lap_time_files:
            raise FileNotFoundError(f"No lap_time file found in {track_path}")
        
        lap_time_file = lap_time_files[0]
        
        # Read CSV
        df = pd.read_csv(lap_time_file)
        
        # Extract vehicle_id and convert to driver_id
        if 'vehicle_id' in df.columns:
            df['driver_id'] = df['vehicle_id'].apply(self._extract_driver_id)
        else:
            raise ValueError("No vehicle_id column found")
        
        # Convert lap time from milliseconds to seconds
        if 'value' in df.columns:
            df['lap_time'] = df['value'] / 1000.0  # Convert ms to seconds
        else:
            raise ValueError("No value column found")
        
        # Handle lap number (filter 32768 errors)
        if 'lap' in df.columns:
            df = df.rename(columns={'lap': 'lap_number'})
            df = df[df['lap_number'] < 1000]  # Filter invalid laps
            df['lap_number'] = df['lap_number'].astype('Int64')
        
        # Sort by driver and lap
        df = df.sort_values(['driver_id', 'lap_number']).reset_index(drop=True)
        
        return df
    
    def _parse_time_to_seconds(self, time_val) -> float:
        """
        Parse time string to seconds
        
        Handles formats like:
        - "2:28.630" (minutes:seconds.milliseconds)
        - "148.630" (seconds.milliseconds)
        - Already a number (assume seconds)
        """
        # Handle NaN/None
        if time_val is None:
            return np.nan
        
        try:
            if pd.isna(time_val):
                return np.nan
        except (ValueError, TypeError):
            pass
        
        # If already a number, return as is (assuming seconds)
        if isinstance(time_val, (int, float)):
            if np.isnan(time_val):
                return np.nan
            return float(time_val)
        
        # Convert to string
        try:
            time_str = str(time_val).strip()
        except:
            return np.nan
        
        # Handle empty string
        if not time_str or time_str == '':
            return np.nan
        
        # Handle MM:SS.mmm format
        if ':' in time_str:
            try:
                parts = time_str.split(':')
                if len(parts) == 2:
                    minutes = float(parts[0])
                    seconds = float(parts[1])
                    return minutes * 60 + seconds
            except (ValueError, IndexError):
                pass
        
        # Handle SS.mmm format
        try:
            return float(time_str)
        except (ValueError, TypeError):
            return np.nan
    
    def _extract_driver_id(self, vehicle_id: str) -> str:
        """
        Extract driver ID from vehicle_id format: GR86-002-2
        Returns: DRIVER_02 (using chassis number)
        """
        if pd.isna(vehicle_id):
            return "UNKNOWN"
        
        vehicle_id = str(vehicle_id)
        
        # Extract chassis number (middle part)
        # Format: GR86-002-2 -> chassis is 002
        match = re.search(r'GR86-(\d+)-', vehicle_id)
        if match:
            chassis = match.group(1)
            return f"DRIVER_{chassis.zfill(2)}"
        
        # Fallback: use car number (last part)
        match = re.search(r'-(\d+)$', vehicle_id)
        if match:
            car_num = match.group(1)
            return f"DRIVER_{car_num.zfill(2)}"
        
        return "UNKNOWN"
    
    def combine_with_results(
        self,
        track: str,
        race: str = "Race 1"
    ) -> pd.DataFrame:
        """
        Combine analysis data with results file for position data
        
        Args:
            track: Track name
            race: Race number
            
        Returns:
            DataFrame with position data added
        """
        if self.race_data is None:
            raise ValueError("Load analysis file first using load_analysis_file()")
        
        track_path = self.data_root / track
        
        # Try multiple structures (same as load_analysis_file)
        results_files = []
        
        # First, try direct subdirectory (COTA, Sonoma)
        race_path = track_path / race
        if race_path.exists() and race_path.is_dir():
            results_files = list(race_path.glob("*Results*.CSV"))
        
        # If not found, check nested subdirectory (road-america/Road America/Race 1/)
        if not results_files:
            for subdir in track_path.iterdir():
                if subdir.is_dir() and not subdir.name.startswith('.'):
                    nested_race_path = subdir / race
                    if nested_race_path.exists() and nested_race_path.is_dir():
                        results_files = list(nested_race_path.glob("*Results*.CSV"))
                        if results_files:
                            break
        
        # If not found, try root-level files (barber, indianapolis style)
        if not results_files:
            race_num = race.replace("Race ", "Race_")
            results_files = list(track_path.glob(f"*Results*{race_num}*"))
            if not results_files:
                results_files = list(track_path.glob(f"*Results*{race}*"))
            
            # Also check in subdirectories
            if not results_files:
                for subdir in track_path.iterdir():
                    if subdir.is_dir():
                        race_num = race.replace("Race ", "Race_")
                        results_files = list(subdir.glob(f"*Results*{race_num}*"))
                        if not results_files:
                            results_files = list(subdir.glob(f"*Results*{race}*"))
                        if results_files:
                            break
        
        if not results_files:
            # Try any results file as fallback
            results_files = list(track_path.glob("*Results*.CSV"))
            # Check subdirectories too
            if not results_files:
                for subdir in track_path.iterdir():
                    if subdir.is_dir():
                        results_files = list(subdir.glob("*Results*.CSV"))
                        if results_files:
                            break
            
            if len(results_files) > 1:
                # Filter by race number if multiple
                if "Race 1" in race or "Race_1" in race:
                    results_files = [f for f in results_files if "Race 2" not in f.name and "Race_2" not in f.name]
                elif "Race 2" in race or "Race_2" in race:
                    results_files = [f for f in results_files if "Race 1" not in f.name and "Race_1" not in f.name]
        
        if not results_files:
            print(f"Warning: No results file found for {track} {race} in {track_path}")
            return self.race_data
        
        results_file = results_files[0]
        
        # Read results (semicolon-separated)
        results_df = pd.read_csv(results_file, sep=';', encoding='utf-8')
        results_df.columns = results_df.columns.str.strip()
        
        # Map car number to position
        if 'NUMBER' in results_df.columns and 'POSITION' in results_df.columns:
            # Handle NaN values in POSITION column
            results_df_clean = results_df[['NUMBER', 'POSITION']].copy()
            results_df_clean = results_df_clean.dropna(subset=['POSITION'])
            
            # Convert to int, handling any edge cases
            try:
                results_df_clean['POSITION'] = pd.to_numeric(results_df_clean['POSITION'], errors='coerce')
                results_df_clean = results_df_clean.dropna(subset=['POSITION'])
                results_df_clean['POSITION'] = results_df_clean['POSITION'].astype(int)
                
                position_map = dict(zip(
                    results_df_clean['NUMBER'].astype(str),
                    results_df_clean['POSITION']
                ))
                
                # Add position to race_data
                if 'car_number' in self.race_data.columns:
                    self.race_data['position'] = self.race_data['car_number'].astype(str).map(
                        position_map
                    )
                    # Fill missing positions with a default
                    if self.race_data['position'].isna().any():
                        max_pos = self.race_data['position'].max()
                        if pd.isna(max_pos):
                            max_pos = 0
                        else:
                            max_pos = int(max_pos)
                        self.race_data['position'] = self.race_data['position'].fillna(max_pos + 1)
                        self.race_data['position'] = self.race_data['position'].astype(int)
            except Exception as e:
                print(f"Warning: Could not map positions: {e}")
                # Set default position if mapping fails
                if 'position' not in self.race_data.columns:
                    self.race_data['position'] = 1
        
        return self.race_data
    
    def get_normalized_data(self) -> pd.DataFrame:
        """
        Get data in normalized format compatible with our feature engineering
        
        Returns:
            DataFrame with columns: lap_number, driver_id, lap_time, sector times, etc.
        """
        if self.race_data is None:
            raise ValueError("Load data first using load_analysis_file()")
        
        # Start with a copy
        df = self.race_data.copy()
        
        # Select only the columns we need (in case there are extra columns)
        columns_to_keep = []
        for col in ['lap_number', 'driver_id', 'lap_time', 
                   'sector_1_time', 'sector_2_time', 'sector_3_time',
                   'position', 'speed_kph']:
            if col in df.columns:
                columns_to_keep.append(col)
        
        df = df[columns_to_keep].copy()
        
        # Add default values for missing columns
        if 'tire_compound' not in df.columns:
            df['tire_compound'] = 'Medium'  # Default
        
        if 'tire_age' not in df.columns:
            # Estimate tire age based on lap number (simplified)
            # Group by driver and calculate laps since start
            df['tire_age'] = df.groupby('driver_id')['lap_number'].transform(
                lambda x: x - x.min()
            )
        
        # Remove rows with invalid lap times
        df = df[df['lap_time'].notna()]
        df = df[df['lap_time'] > 0]
        df = df[df['lap_time'] < 600]  # Reasonable max (10 minutes)
        
        return df.reset_index(drop=True)
    
    def list_available_tracks(self) -> List[str]:
        """List all available tracks in the dataset"""
        tracks = []
        for item in self.data_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                tracks.append(item.name)
        return sorted(tracks)
    
    def list_races_for_track(self, track: str) -> List[str]:
        """
        List available races for a track
        
        Handles three structures:
        1. Track/Race 1/, Track/Race 2/ (COTA, Sonoma style)
        2. Track/*Race 1*, Track/*Race 2* (barber, indianapolis style)
        3. Track/Subfolder/Race 1/ (road-america/Road America, sebring/Sebring style)
        """
        track_path = self.data_root / track
        races = []
        race_set = set()
        
        # Check for direct subdirectory structure (COTA, Sonoma style)
        for item in track_path.iterdir():
            if item.is_dir() and 'Race' in item.name:
                races.append(item.name)
                race_set.add(item.name)
        
        # Check for nested subdirectory structure (road-america/Road America/Race 1/)
        for subdir in track_path.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                for item in subdir.iterdir():
                    if item.is_dir() and 'Race' in item.name:
                        if item.name not in race_set:
                            races.append(item.name)
                            race_set.add(item.name)
        
        # Check for files with race numbers in name (barber, indianapolis style)
        # Check root level
        analysis_files = list(track_path.glob("*AnalysisEnduranceWithSections*"))
        # Also check subdirectories
        for subdir in track_path.iterdir():
            if subdir.is_dir():
                analysis_files.extend(list(subdir.glob("*AnalysisEnduranceWithSections*")))
        
        for file in analysis_files:
            file_name = file.name
            # Extract race number from filename
            if "Race 1" in file_name or "Race_1" in file_name:
                if "Race 1" not in race_set:
                    races.append("Race 1")
                    race_set.add("Race 1")
            elif "Race 2" in file_name or "Race_2" in file_name:
                if "Race 2" not in race_set:
                    races.append("Race 2")
                    race_set.add("Race 2")
            elif len(analysis_files) == 1:
                # Single file, no race number - treat as Race 1
                if "Race 1" not in race_set:
                    races.append("Race 1")
                    race_set.add("Race 1")
        
        # If no races found, default to Race 1
        if not races:
            races = ["Race 1"]
        
        return sorted(races)

