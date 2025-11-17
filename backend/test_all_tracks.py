"""
Test script to verify all tracks load correctly
Tests both folder structures and logs results
"""

import sys
from pathlib import Path
import traceback
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from trd_data_loader import TRDDataLoader
from feature_engineering import FeatureEngineer
from ml_models import RaceStrategyPredictor

def test_track(track_name, race_name, trd_loader):
    """Test loading a specific track and race"""
    print(f"\n{'='*60}")
    print(f"Testing: {track_name} - {race_name}")
    print(f"{'='*60}")
    
    try:
        # Load analysis file
        df = trd_loader.load_analysis_file(track=track_name, race=race_name)
        print(f"✓ Loaded {len(df)} lap records")
        
        # Combine with results
        df = trd_loader.combine_with_results(track=track_name, race=race_name)
        print(f"✓ Combined with results")
        
        # Get normalized data
        normalized_df = trd_loader.get_normalized_data()
        print(f"✓ Normalized: {len(normalized_df)} records")
        print(f"  Drivers: {normalized_df['driver_id'].nunique()}")
        print(f"  Lap range: {normalized_df['lap_number'].min()}-{normalized_df['lap_number'].max()}")
        
        # Test feature engineering
        fe = FeatureEngineer(normalized_df)
        driver_id = normalized_df['driver_id'].iloc[0]
        current_lap = normalized_df['lap_number'].max() // 2
        
        twi = fe.calculate_tire_wear_index(driver_id, current_lap)
        print(f"✓ Tire Wear Index: {twi.current_twi:.2f}")
        
        consistency = fe.calculate_consistency_score(driver_id)
        print(f"✓ Consistency Score: {consistency.consistency_score:.2f}")
        
        # Test strategy prediction
        predictor = RaceStrategyPredictor(fe)
        total_laps = normalized_df['lap_number'].max()
        pit_window = predictor.predict_pit_window(driver_id, current_lap, total_laps)
        print(f"✓ Pit Window: Laps {pit_window.pit_window_start}-{pit_window.pit_window_end}")
        
        print(f"✅ {track_name} - {race_name}: SUCCESS")
        return True
        
    except Exception as e:
        print(f"✗ {track_name} - {race_name}: FAILED")
        print(f"  Error: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Test all tracks"""
    print("\n" + "="*60)
    print("GR Race Strategist AI - Track Loading Test Suite")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize loader
    trd_loader = TRDDataLoader(data_root="Data-GR")
    
    # List all tracks
    tracks = trd_loader.list_available_tracks()
    print(f"Found {len(tracks)} tracks: {', '.join(tracks)}\n")
    
    results = {}
    total_tests = 0
    passed_tests = 0
    
    # Test each track
    for track in tracks:
        print(f"\n{'#'*60}")
        print(f"Testing Track: {track}")
        print(f"{'#'*60}")
        
        # List races for this track
        races = trd_loader.list_races_for_track(track)
        print(f"Available races: {races}")
        
        results[track] = {}
        
        for race in races:
            total_tests += 1
            success = test_track(track, race, trd_loader)
            results[track][race] = success
            if success:
                passed_tests += 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Detailed results
    print("\n" + "="*60)
    print("DETAILED RESULTS")
    print("="*60)
    for track, race_results in results.items():
        for race, success in race_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} - {track} / {race}")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

