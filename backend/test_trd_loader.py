"""
Test script for TRD data loader
Run this to verify TRD data loading works correctly
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from trd_data_loader import TRDDataLoader
from feature_engineering import FeatureEngineer
from ml_models import RaceStrategyPredictor

def test_load_cota():
    """Test loading COTA Race 1 data"""
    print("=" * 60)
    print("Testing TRD Data Loader - COTA Race 1")
    print("=" * 60)
    
    # Initialize loader
    trd_loader = TRDDataLoader(data_root="Data-GR")
    
    # List available tracks
    print("\n1. Available tracks:")
    tracks = trd_loader.list_available_tracks()
    print(f"   {tracks}")
    
    # List races for COTA
    print("\n2. Available races for COTA:")
    races = trd_loader.list_races_for_track("COTA")
    print(f"   {races}")
    
    # Load COTA Race 1
    print("\n3. Loading COTA Race 1 data...")
    try:
        df = trd_loader.load_analysis_file(track="COTA", race="Race 1")
        print(f"   ✓ Loaded {len(df)} lap records")
        print(f"   ✓ Drivers: {df['driver_id'].unique()[:5]}...")  # Show first 5
        
        # Combine with results
        df = trd_loader.combine_with_results(track="COTA", race="Race 1")
        print(f"   ✓ Combined with results data")
        
        # Get normalized data
        normalized_df = trd_loader.get_normalized_data()
        print(f"   ✓ Normalized data: {len(normalized_df)} records")
        print(f"   ✓ Columns: {list(normalized_df.columns)}")
        
        # Show sample
        print("\n4. Sample data:")
        print(normalized_df.head())
        
        # Test feature engineering
        print("\n5. Testing feature engineering...")
        fe = FeatureEngineer(normalized_df)
        
        # Get first driver
        driver_id = normalized_df['driver_id'].iloc[0]
        current_lap = normalized_df['lap_number'].max() // 2  # Middle of race
        
        print(f"\n   Testing with driver: {driver_id}, lap: {current_lap}")
        
        # Tire Wear Index
        twi = fe.calculate_tire_wear_index(driver_id, current_lap)
        print(f"   ✓ Tire Wear Index: {twi.current_twi:.2f}")
        print(f"     Degradation Rate: {twi.degradation_rate:.2f} TWI/lap")
        print(f"     Optimal Pit Lap: {twi.optimal_pit_lap}")
        
        # Consistency
        consistency = fe.calculate_consistency_score(driver_id)
        print(f"   ✓ Consistency Score: {consistency.consistency_score:.2f}")
        print(f"     Trend: {consistency.recent_trend}")
        
        # Track Evolution
        track_evo = fe.calculate_track_evolution()
        print(f"   ✓ Track Evolution: {track_evo.evolution_rate:.4f} s/lap")
        print(f"     Grip Level: {track_evo.track_grip_level:.2f}")
        
        # Strategy prediction
        print("\n6. Testing strategy predictions...")
        predictor = RaceStrategyPredictor(fe)
        
        total_laps = normalized_df['lap_number'].max()
        pit_window = predictor.predict_pit_window(driver_id, current_lap, total_laps)
        print(f"   ✓ Pit Window: Laps {pit_window.pit_window_start}-{pit_window.pit_window_end}")
        print(f"     Optimal: Lap {pit_window.optimal_pit_lap}")
        print(f"     Urgency: {pit_window.urgency}")
        print(f"     Recommended Compound: {pit_window.tire_compound_recommendation}")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_load_cota()
    sys.exit(0 if success else 1)

