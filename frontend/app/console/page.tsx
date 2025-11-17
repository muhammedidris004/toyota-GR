'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Navigation from '../components/Navigation'
import ConsoleStepper from '../components/ConsoleStepper'
import TireWearChart from '../components/TireWearChart'
import PaceProjectionChart from '../components/PaceProjectionChart'
import { 
  getDataInfo, 
  getStrategy, 
  getUndercut,
  loadTRDData, 
  listTRDTracks,
  listTRDRaces,
  type StrategyResponse,
  type DataInfo,
  type UndercutSimulation
} from '../../lib/api'

function RaceEngineerConsoleContent() {
  const searchParams = useSearchParams()
  const [dataInfo, setDataInfo] = useState<DataInfo | null>(null)
  const [strategy, setStrategy] = useState<StrategyResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const [selectedTrack, setSelectedTrack] = useState('COTA')
  const [selectedRace, setSelectedRace] = useState('Race 1')
  const [selectedDriver, setSelectedDriver] = useState('')
  const [currentLap, setCurrentLap] = useState(8)
  const [totalLaps, setTotalLaps] = useState(17)
  
  const [tracks, setTracks] = useState<string[]>([])
  const [races, setRaces] = useState<string[]>([])
  const [demoMode, setDemoMode] = useState(false)
  
  // Feature 3: Undercut Simulation State
  const [undercutSimulation, setUndercutSimulation] = useState<UndercutSimulation | null>(null)
  const [undercutLoading, setUndercutLoading] = useState(false)
  const [undercutError, setUndercutError] = useState<string | null>(null)
  const [targetDriver, setTargetDriver] = useState('')

  // Load tracks on mount
  useEffect(() => {
    listTRDTracks()
      .then(res => setTracks(res.tracks || []))
      .catch(err => console.error('Failed to load tracks:', err))
  }, [])

  // Load races when track changes
  useEffect(() => {
    if (selectedTrack) {
      listTRDRaces(selectedTrack)
        .then(res => setRaces(res.races || []))
        .catch(err => console.error('Failed to load races:', err))
    }
  }, [selectedTrack])

  // Auto-load handler for demo scenario (Feature 1: One-Click Demo Scenario)
  const handleAutoLoadDemo = async (track: string, race: string, driver: string, lap: number) => {
    setLoading(true)
    setError(null)
    try {
      // Load TRD data
      await loadTRDData(track, race)
      
      // Get data info
      const info = await getDataInfo()
      setDataInfo(info)
      
      // Set driver if provided, otherwise use first available
      const finalDriver = driver || (info.drivers.length > 0 ? info.drivers[0] : '')
      if (finalDriver) {
        setSelectedDriver(finalDriver)
        setTotalLaps(info.lap_range.max)
        setCurrentLap(lap)
        
        // Auto-load strategy
        const strategyData = await getStrategy(finalDriver, lap, info.lap_range.max)
        setStrategy(strategyData)
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load demo scenario')
    } finally {
      setLoading(false)
    }
  }

  // Check for demo mode from query params (Feature 1: One-Click Demo Scenario)
  useEffect(() => {
    const demo = searchParams.get('demo')
    const track = searchParams.get('track')
    const race = searchParams.get('race')
    const driver = searchParams.get('driver')
    const lap = searchParams.get('lap')
    
    if (demo === 'true' && track && race) {
      // Demo mode: auto-load data and strategy
      setDemoMode(true)
      setSelectedTrack(track)
      setSelectedRace(race)
      if (driver) setSelectedDriver(driver)
      if (lap) setCurrentLap(parseInt(lap) || 8)
      
      // Auto-load data
      handleAutoLoadDemo(track, race, driver || '', parseInt(lap || '8'))
    } else {
      // Normal mode: just load data info
      loadDataInfo()
    }
  }, [searchParams])
  
  // Load data info on mount (only if not in demo mode)
  useEffect(() => {
    if (!demoMode) {
      loadDataInfo()
    }
  }, [demoMode])

  const loadDataInfo = async () => {
    try {
      const info = await getDataInfo()
      setDataInfo(info)
      if (info.drivers.length > 0 && !selectedDriver) {
        setSelectedDriver(info.drivers[0])
        setTotalLaps(info.lap_range.max)
      }
    } catch (err) {
      console.error('Failed to load data info:', err)
    }
  }

  const handleLoadData = async () => {
    setLoading(true)
    setError(null)
    try {
      await loadTRDData(selectedTrack, selectedRace)
      await loadDataInfo()
    } catch (err: any) {
      setError(err.message || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleGetStrategy = async () => {
    if (!selectedDriver) {
      setError('Please select a driver')
      return
    }
    
    setLoading(true)
    setError(null)
    try {
      const strategyData = await getStrategy(selectedDriver, currentLap, totalLaps)
      setStrategy(strategyData)
    } catch (err: any) {
      setError(err.message || 'Failed to get strategy')
    } finally {
      setLoading(false)
    }
  }

  // Feature 3: Undercut Simulation Handler
  const handleUndercutSimulation = async () => {
    if (!selectedDriver) {
      setUndercutError('Please select your driver first')
      return
    }
    if (!targetDriver) {
      setUndercutError('Please select a target driver')
      return
    }
    if (selectedDriver === targetDriver) {
      setUndercutError('Your driver and target driver must be different')
      return
    }
    
    setUndercutLoading(true)
    setUndercutError(null)
    try {
      const simulation = await getUndercut(selectedDriver, targetDriver, currentLap, totalLaps)
      setUndercutSimulation(simulation)
    } catch (err: any) {
      setUndercutError(err.message || 'Failed to simulate undercut')
      setUndercutSimulation(null)
    } finally {
      setUndercutLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gr-black">
      <Navigation />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gr-neon mb-2">Race Engineer Console</h1>
          <p className="text-gr-grey">Real-time race strategy and performance monitoring</p>
        </div>

        {/* Feature 2: Console Flow Stepper - Visual progress indicator */}
        <ConsoleStepper
          step1Complete={selectedTrack !== '' && selectedRace !== ''}
          step2Complete={dataInfo?.loaded || false}
          step3Complete={selectedDriver !== ''}
          step4Complete={strategy !== null}
        />

        {/* Data Loading Section */}
        <div className="bg-gr-asphalt rounded-lg p-6 mb-6 border border-gr-grey">
          <h2 className="text-2xl font-semibold text-white mb-4">Load Race Data</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gr-grey mb-2">Track</label>
              <select
                value={selectedTrack}
                onChange={(e) => setSelectedTrack(e.target.value)}
                className="w-full bg-gr-grey text-white rounded-lg px-4 py-2 border border-gr-grey focus:border-gr-red focus:outline-none"
              >
                {tracks.map(track => (
                  <option key={track} value={track}>{track}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gr-grey mb-2">Race</label>
              <select
                value={selectedRace}
                onChange={(e) => setSelectedRace(e.target.value)}
                className="w-full bg-gr-grey text-white rounded-lg px-4 py-2 border border-gr-grey focus:border-gr-red focus:outline-none"
              >
                {races.map(race => (
                  <option key={race} value={race}>{race}</option>
                ))}
              </select>
            </div>
            
            <div className="flex items-end">
                <button
                  onClick={handleLoadData}
                  disabled={loading}
                  className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                      Loading Data...
                    </span>
                  ) : (
                    'Load Data'
                  )}
                </button>
            </div>
          </div>

          {dataInfo && (
            <div className="mt-4 p-4 bg-gr-grey/30 border border-gr-neon/30 rounded-lg">
              <p className="text-sm text-white flex items-center gap-2">
                <svg className="w-4 h-4 text-gr-neon" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Loaded: {dataInfo.drivers.length} drivers, Laps {dataInfo.lap_range.min}-{dataInfo.lap_range.max}</span>
              </p>
            </div>
          )}
        </div>

        {/* Strategy Input Section */}
        {dataInfo && dataInfo.loaded ? (
          <div className="card p-8 mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">Strategy Analysis</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gr-grey mb-2">Driver</label>
                <select
                  value={selectedDriver}
                  onChange={(e) => setSelectedDriver(e.target.value)}
                  className="input-field w-full"
                >
                  {dataInfo.drivers.map(driver => (
                    <option key={driver} value={driver}>{driver}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gr-grey mb-2">Current Lap</label>
                <input
                  type="number"
                  value={currentLap}
                  onChange={(e) => setCurrentLap(parseInt(e.target.value) || 1)}
                  min={1}
                  max={totalLaps}
                  className="input-field w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gr-grey mb-2">Total Laps</label>
                <input
                  type="number"
                  value={totalLaps}
                  onChange={(e) => setTotalLaps(parseInt(e.target.value) || 1)}
                  min={1}
                  className="input-field w-full"
                />
              </div>
              
              <div className="flex items-end">
                <button
                  onClick={handleGetStrategy}
                  disabled={loading}
                  className="w-full bg-gr-neon-gradient hover:shadow-gr-neon text-gr-black font-semibold py-3 px-6 rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <span className="w-4 h-4 border-2 border-gr-black/30 border-t-gr-black rounded-full animate-spin"></span>
                      Analyzing Strategy...
                    </span>
                  ) : (
                    'Get Strategy'
                  )}
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="card p-8 mb-8 opacity-60">
            <h2 className="text-2xl font-semibold text-white mb-4">Strategy Analysis</h2>
            <p className="text-gr-grey text-center py-8">
              Load a track & race to enable strategy analysis
            </p>
          </div>
        )}

        {error && (
          <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Strategy Results */}
        {strategy && (
          <div className="space-y-6">
            {/* Tire Wear */}
            <div className="card p-8">
              <h3 className="text-xl font-semibold text-white mb-4">Tire Wear Analysis</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div>
                  <p className="text-sm text-gr-grey">Current TWI</p>
                  <p className="text-2xl font-bold text-gr-neon">{strategy.tire_wear.current_twi.toFixed(1)}</p>
                </div>
                <div>
                  <p className="text-sm text-gr-grey">Degradation Rate</p>
                  <p className="text-2xl font-bold text-white">{strategy.tire_wear.degradation_rate.toFixed(2)}/lap</p>
                </div>
                <div>
                  <p className="text-sm text-gr-grey">Optimal Pit Lap</p>
                  <p className="text-2xl font-bold text-gr-red">{strategy.tire_wear.optimal_pit_lap || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gr-grey">Projected TWI</p>
                  <p className="text-2xl font-bold text-white">{strategy.tire_wear.projected_twi.toFixed(1)}</p>
                </div>
              </div>
              {/* Tire Wear Chart */}
              <div className="mt-4">
                <TireWearChart 
                  data={Array.from({ length: totalLaps }, (_, i) => {
                    const lap = i + 1
                    const twi = Math.max(0, Math.min(100, 
                      strategy.tire_wear.current_twi + 
                      (lap - currentLap) * strategy.tire_wear.degradation_rate
                    ))
                    return {
                      lap,
                      twi: twi,
                      degradationRate: strategy.tire_wear.degradation_rate
                    }
                  })}
                  currentLap={currentLap}
                />
              </div>
            </div>

            {/* Pit Window */}
            <div className="card p-8">
              <h3 className="text-xl font-semibold text-white mb-4">Pit Window Recommendation</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="metric-card">
                  <p className="text-sm text-gr-grey mb-1">Optimal Pit Lap</p>
                  <p className="text-3xl font-bold text-gr-neon">{strategy.pit_window.optimal_pit_lap}</p>
                </div>
                <div className="metric-card">
                  <p className="text-sm text-gr-grey mb-1">Window</p>
                  <p className="text-2xl font-bold text-white">
                    Laps {strategy.pit_window.pit_window_start}-{strategy.pit_window.pit_window_end}
                  </p>
                </div>
                <div className="metric-card">
                  <p className="text-sm text-gr-grey mb-1">Urgency</p>
                  <p className={`text-2xl font-bold ${
                    strategy.pit_window.urgency === 'critical' ? 'text-red-500' :
                    strategy.pit_window.urgency === 'high' ? 'text-orange-500' :
                    strategy.pit_window.urgency === 'medium' ? 'text-yellow-500' :
                    'text-green-500'
                  }`}>
                    {strategy.pit_window.urgency.toUpperCase()}
                  </p>
                </div>
              </div>
              <div className="mt-4">
                <p className="text-gr-grey text-sm">Reason: {strategy.pit_window.reason}</p>
                <p className="text-gr-neon text-sm mt-1">
                  Recommended Compound: {strategy.pit_window.tire_compound_recommendation}
                </p>
              </div>
            </div>

            {/* Pace Projection */}
            <div className="card p-8">
              <h3 className="text-xl font-semibold text-white mb-4">Pace Projection</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-2 mb-6">
                {strategy.pace_projection.projected_laps.slice(0, 10).map((proj, idx) => (
                  <div key={idx} className="metric-card text-center">
                    <p className="text-xs text-gr-grey">Lap {proj.lap}</p>
                    <p className="text-lg font-bold text-white">{proj.pace.toFixed(2)}s</p>
                  </div>
                ))}
              </div>
              {/* Pace Projection Chart */}
              <div className="mt-4">
                <PaceProjectionChart 
                  data={strategy.pace_projection.projected_laps.map(proj => ({
                    lap: proj.lap,
                    projectedPace: proj.pace
                  }))}
                  currentLap={currentLap}
                />
              </div>
            </div>

            {/* Consistency & Traffic */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="card p-8">
                <h3 className="text-xl font-semibold text-white mb-4">Driver Consistency</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gr-grey">Score</span>
                    <span className="text-2xl font-bold text-gr-neon">{strategy.consistency.consistency_score.toFixed(1)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gr-grey">Trend</span>
                    <span className="text-white">{strategy.consistency.recent_trend}</span>
                  </div>
                </div>
              </div>

              <div className="card p-8">
                <h3 className="text-xl font-semibold text-white mb-4">Traffic Impact</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gr-grey">Traffic Loss</span>
                    <span className="text-2xl font-bold text-gr-red">+{strategy.traffic_loss.traffic_loss.toFixed(2)}s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gr-grey">Cars Ahead</span>
                    <span className="text-white">{strategy.traffic_loss.cars_ahead}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gr-grey">Overtake Opportunity</span>
                    <span className={strategy.traffic_loss.overtake_opportunity ? 'text-gr-neon' : 'text-gr-grey'}>
                      {strategy.traffic_loss.overtake_opportunity ? 'Yes' : 'No'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Feature 3: Dedicated Undercut Simulation UI */}
            {dataInfo && dataInfo.loaded && (
              <div className="card p-8">
                <h3 className="text-2xl font-bold text-white mb-6">Undercut Simulation</h3>
                <p className="text-gr-grey mb-6">
                  Simulate an undercut/overcut strategy against a specific driver to see potential gains
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div>
                    <label className="block text-sm font-medium text-gr-grey mb-2">Your Driver</label>
                    <select
                      value={selectedDriver}
                      onChange={(e) => setSelectedDriver(e.target.value)}
                      className="input-field w-full"
                      disabled={!dataInfo?.loaded}
                    >
                      {dataInfo?.drivers.map(driver => (
                        <option key={driver} value={driver}>{driver}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gr-grey mb-2">Target Driver</label>
                    <select
                      value={targetDriver}
                      onChange={(e) => setTargetDriver(e.target.value)}
                      className="input-field w-full"
                      disabled={!dataInfo?.loaded}
                    >
                      <option value="">Select target driver...</option>
                      {dataInfo?.drivers
                        .filter(d => d !== selectedDriver)
                        .map(driver => (
                          <option key={driver} value={driver}>{driver}</option>
                        ))}
                    </select>
                  </div>
                  
                  <div className="flex items-end">
                    <button
                      onClick={handleUndercutSimulation}
                      disabled={undercutLoading || !selectedDriver || !targetDriver}
                      className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {undercutLoading ? (
                        <span className="flex items-center justify-center gap-2">
                          <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                          Simulating...
                        </span>
                      ) : (
                        'Simulate Undercut'
                      )}
                    </button>
                  </div>
                </div>

                {undercutError && (
                  <div className="bg-red-900/30 border border-red-700 text-red-200 px-4 py-3 rounded-lg mb-4">
                    {undercutError}
                  </div>
                )}

                {undercutSimulation && (
                  <div className="bg-gr-neon/10 border-2 border-gr-neon/50 rounded-lg p-6 space-y-4">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-xl font-bold text-gr-neon">
                        {undercutSimulation.strategy_type.toUpperCase()} Simulation Results
                      </h4>
                      <div className={`px-4 py-2 rounded-lg font-bold ${
                        undercutSimulation.success_probability > 0.7
                          ? 'bg-gr-neon text-gr-black'
                          : undercutSimulation.success_probability > 0.5
                          ? 'bg-yellow-500 text-black'
                          : 'bg-gr-grey text-white'
                      }`}>
                        {(undercutSimulation.success_probability * 100).toFixed(0)}% Success
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="metric-card">
                        <p className="text-xs uppercase tracking-wider text-gr-grey mb-2">Expected Gain</p>
                        <p className="text-3xl font-bold text-gr-neon">
                          +{undercutSimulation.expected_gain.toFixed(2)}s
                        </p>
                        <p className="text-xs text-gr-grey mt-1">after 3 laps</p>
                      </div>
                      
                      <div className="metric-card">
                        <p className="text-xs uppercase tracking-wider text-gr-grey mb-2">Optimal Pit Lap</p>
                        <p className="text-3xl font-bold text-white">
                          {undercutSimulation.optimal_pit_lap}
                        </p>
                      </div>
                      
                      <div className="metric-card">
                        <p className="text-xs uppercase tracking-wider text-gr-grey mb-2">Strategy Type</p>
                        <p className="text-lg font-bold text-white">
                          {undercutSimulation.strategy_type}
                        </p>
                      </div>
                      
                      <div className="metric-card">
                        <p className="text-xs uppercase tracking-wider text-gr-grey mb-2">Target Driver</p>
                        <p className="text-lg font-bold text-gr-red">
                          {undercutSimulation.target_driver_id}
                        </p>
                      </div>
                    </div>

                    {undercutSimulation.risk_factors && undercutSimulation.risk_factors.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-gr-grey/30">
                        <p className="text-sm font-semibold text-gr-grey mb-2">Risk Factors:</p>
                        <ul className="list-disc list-inside text-sm text-gr-grey space-y-1">
                          {undercutSimulation.risk_factors.map((risk, idx) => (
                            <li key={idx}>{risk}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Undercut Opportunities (from strategy response) */}
            {strategy && strategy.undercut_opportunities.length > 0 && (
              <div className="card p-8">
                <h3 className="text-xl font-semibold text-white mb-4">Auto-Detected Undercut Opportunities</h3>
                <div className="space-y-3">
                  {strategy.undercut_opportunities.map((undercut, idx) => (
                    <div key={idx} className="bg-gr-grey/30 rounded-lg p-4 border border-gr-grey/50">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-white font-semibold">
                            {undercut.strategy_type.toUpperCase()} vs {undercut.target_driver_id}
                          </p>
                          <p className="text-sm text-gr-grey">Optimal Pit Lap: {undercut.optimal_pit_lap}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-gr-neon font-bold">+{undercut.expected_gain.toFixed(2)}s</p>
                          <p className="text-sm text-gr-grey">
                            {(undercut.success_probability * 100).toFixed(0)}% success
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

// Wrap in Suspense for useSearchParams (Next.js App Router requirement)
export default function RaceEngineerConsole() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gr-black flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl font-bold bg-gradient-to-r from-gr-red to-gr-neon bg-clip-text text-transparent mb-4 animate-pulse-slow">
            GR
          </div>
          <div className="text-white text-lg">Loading Race Engineer Console...</div>
        </div>
      </div>
    }>
      <RaceEngineerConsoleContent />
    </Suspense>
  )
}

