/**
 * API Client for GR Race Strategist AI
 * Handles all backend API calls
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://toyota-gr.onrender.com';

export interface TireWearIndex {
  driver_id: string;
  current_twi: number;
  projected_twi: number;
  degradation_rate: number;
  optimal_pit_lap: number | null;
}

export interface DriverConsistencyScore {
  driver_id: string;
  consistency_score: number;
  lap_time_variance: number;
  sector_variance: Record<string, number>;
  recent_trend: string;
}

export interface TrafficLossFactor {
  driver_id: string;
  traffic_loss: number;
  cars_ahead: number;
  dirty_air_factor: number;
  overtake_opportunity: boolean;
}

export interface TrackEvolutionRate {
  evolution_rate: number;
  track_grip_level: number;
  rubber_laying_effect: number;
  projected_optimal_lap: number | null;
}

export interface PaceDeltaTrend {
  driver_id: string;
  current_pace_delta: number;
  pace_trend: number[];
  trend_direction: string;
  projected_pace: number;
}

export interface PitWindowRecommendation {
  driver_id: string;
  optimal_pit_lap: number;
  pit_window_start: number;
  pit_window_end: number;
  urgency: string;
  reason: string;
  estimated_time_loss: number;
  tire_compound_recommendation: string;
}

export interface UndercutSimulation {
  driver_id: string;
  target_driver_id: string;
  strategy_type: string;
  optimal_pit_lap: number;
  expected_gain: number;
  success_probability: number;
  risk_factors: string[];
}

export interface PaceProjection {
  driver_id: string;
  current_lap: number;
  projected_laps: Array<{ lap: number; pace: number }>;
  factors_considered: string[];
  confidence: number;
}

export interface StrategyResponse {
  driver_id: string;
  tire_wear: TireWearIndex;
  pace_projection: PaceProjection;
  pit_window: PitWindowRecommendation;
  undercut_opportunities: UndercutSimulation[];
  consistency: DriverConsistencyScore;
  traffic_loss: TrafficLossFactor;
}

export interface DataInfo {
  loaded: boolean;
  drivers: string[];
  lap_range: {
    min: number;
    max: number;
  };
  validation: {
    loaded: boolean;
    total_laps: number;
    unique_drivers: number;
    missing_lap_times: number;
    negative_lap_times: number;
    duplicate_laps: number;
  };
}

// API Functions
export async function loadSampleData(numDrivers: number = 5, numLaps: number = 50) {
  const response = await fetch(`${API_BASE_URL}/api/data/load-sample?num_drivers=${numDrivers}&num_laps=${numLaps}`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to load sample data');
  return response.json();
}

export async function loadTRDData(track: string, race: string = 'Race 1') {
  const response = await fetch(`${API_BASE_URL}/api/data/load-trd?track=${encodeURIComponent(track)}&race=${encodeURIComponent(race)}`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to load TRD data');
  return response.json();
}

export async function getDataInfo(): Promise<DataInfo> {
  const response = await fetch(`${API_BASE_URL}/api/data/info`);
  if (!response.ok) throw new Error('Failed to get data info');
  return response.json();
}

export async function listTRDTracks() {
  const response = await fetch(`${API_BASE_URL}/api/data/trd/tracks`);
  if (!response.ok) throw new Error('Failed to list tracks');
  return response.json();
}

export async function listTRDRaces(track: string) {
  const response = await fetch(`${API_BASE_URL}/api/data/trd/races/${encodeURIComponent(track)}`);
  if (!response.ok) throw new Error('Failed to list races');
  return response.json();
}

export async function getTireWear(driverId: string, currentLap?: number): Promise<TireWearIndex> {
  const url = `${API_BASE_URL}/api/features/tire-wear/${encodeURIComponent(driverId)}${currentLap ? `?current_lap=${currentLap}` : ''}`;
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to get tire wear');
  return response.json();
}

export async function getConsistency(driverId: string, window: number = 10): Promise<DriverConsistencyScore> {
  const response = await fetch(`${API_BASE_URL}/api/features/consistency/${encodeURIComponent(driverId)}?window=${window}`);
  if (!response.ok) throw new Error('Failed to get consistency');
  return response.json();
}

export async function getTrafficLoss(driverId: string, currentLap?: number): Promise<TrafficLossFactor> {
  const url = `${API_BASE_URL}/api/features/traffic/${encodeURIComponent(driverId)}${currentLap ? `?current_lap=${currentLap}` : ''}`;
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to get traffic loss');
  return response.json();
}

export async function getTrackEvolution(window: number = 20): Promise<TrackEvolutionRate> {
  const response = await fetch(`${API_BASE_URL}/api/features/track-evolution?window=${window}`);
  if (!response.ok) throw new Error('Failed to get track evolution');
  return response.json();
}

export async function getPaceDelta(driverId: string, window: number = 10): Promise<PaceDeltaTrend> {
  const response = await fetch(`${API_BASE_URL}/api/features/pace-delta/${encodeURIComponent(driverId)}?window=${window}`);
  if (!response.ok) throw new Error('Failed to get pace delta');
  return response.json();
}

export async function getStrategy(
  driverId: string,
  currentLap: number,
  totalLaps: number = 50,
  includeUndercut: boolean = true
): Promise<StrategyResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/strategy/${encodeURIComponent(driverId)}?current_lap=${currentLap}&total_laps=${totalLaps}&include_undercut=${includeUndercut}`
  );
  if (!response.ok) throw new Error('Failed to get strategy');
  return response.json();
}

export async function getPitWindow(driverId: string, currentLap: number, totalLaps: number = 50): Promise<PitWindowRecommendation> {
  const response = await fetch(
    `${API_BASE_URL}/api/strategy/pit-window/${encodeURIComponent(driverId)}?current_lap=${currentLap}&total_laps=${totalLaps}`
  );
  if (!response.ok) throw new Error('Failed to get pit window');
  return response.json();
}

export async function getPaceProjection(driverId: string, currentLap: number, projectionLaps: number = 10): Promise<PaceProjection> {
  const response = await fetch(
    `${API_BASE_URL}/api/strategy/pace-projection/${encodeURIComponent(driverId)}?current_lap=${currentLap}&projection_laps=${projectionLaps}`
  );
  if (!response.ok) throw new Error('Failed to get pace projection');
  return response.json();
}

export async function getUndercut(
  driverId: string,
  targetDriverId: string,
  currentLap: number,
  totalLaps: number = 50
): Promise<UndercutSimulation> {
  const response = await fetch(
    `${API_BASE_URL}/api/strategy/undercut/${encodeURIComponent(driverId)}/${encodeURIComponent(targetDriverId)}?current_lap=${currentLap}&total_laps=${totalLaps}`
  );
  if (!response.ok) throw new Error('Failed to get undercut simulation');
  return response.json();
}

