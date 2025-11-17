'use client'

import { useState, useEffect } from 'react'
import Navigation from '../components/Navigation'
import { 
  getDataInfo, 
  getPitWindow,
  getPaceProjection,
  type DataInfo,
  type PitWindowRecommendation,
  type PaceProjection
} from '../../lib/api'

export default function StrategyReplay() {
  const [dataInfo, setDataInfo] = useState<DataInfo | null>(null)
  const [selectedDriver, setSelectedDriver] = useState('')
  const [currentLap, setCurrentLap] = useState(1)
  const [totalLaps, setTotalLaps] = useState(17)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const [pitWindows, setPitWindows] = useState<PitWindowRecommendation[]>([])
  const [paceProjections, setPaceProjections] = useState<PaceProjection[]>([])
  const [replayData, setReplayData] = useState<Array<{
    lap: number;
    pitWindow: PitWindowRecommendation | null;
    paceProjection: PaceProjection | null;
  }>>([])

  useEffect(() => {
    loadDataInfo()
  }, [])

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

  const loadReplayData = async () => {
    if (!selectedDriver || !dataInfo?.loaded) return

    setLoading(true)
    setError(null)
    
    try {
      const replay: Array<{ lap: number; pitWindow: PitWindowRecommendation | null; paceProjection: PaceProjection | null }> = []
      
      // Load data for each lap (sample every 2 laps for performance)
      for (let lap = 1; lap <= totalLaps; lap += 2) {
        try {
          const [pitWindow, paceProjection] = await Promise.all([
            getPitWindow(selectedDriver, lap, totalLaps).catch(() => null),
            getPaceProjection(selectedDriver, lap, 5).catch(() => null),
          ])
          
          replay.push({ lap, pitWindow, paceProjection })
        } catch (err) {
          console.error(`Error loading lap ${lap}:`, err)
        }
      }
      
      setReplayData(replay)
    } catch (err: any) {
      setError(err.message || 'Failed to load replay data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (selectedDriver && dataInfo?.loaded) {
      loadReplayData()
    }
  }, [selectedDriver, totalLaps, dataInfo])

  const handleLapChange = (lap: number) => {
    setCurrentLap(lap)
  }

  const currentReplayPoint = replayData.find(r => r.lap === currentLap) || 
                            replayData.find(r => r.lap <= currentLap && r.lap + 2 > currentLap) ||
                            replayData[0]

  return (
    <div className="min-h-screen bg-gr-black">
      <Navigation />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gr-neon mb-2">Strategy Replay</h1>
          <p className="text-gr-grey">Review and analyze race strategy evolution over time</p>
        </div>

        {/* Controls */}
        <div className="bg-gr-asphalt rounded-lg p-6 mb-6 border border-gr-grey">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gr-grey mb-2">Driver</label>
              <select
                value={selectedDriver}
                onChange={(e) => setSelectedDriver(e.target.value)}
                className="w-full bg-gr-grey text-white rounded-lg px-4 py-2 border border-gr-grey focus:border-gr-red focus:outline-none"
              >
                {dataInfo?.drivers.map(driver => (
                  <option key={driver} value={driver}>{driver}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gr-grey mb-2">Total Laps</label>
              <input
                type="number"
                value={totalLaps}
                onChange={(e) => setTotalLaps(parseInt(e.target.value) || 1)}
                min={1}
                className="w-full bg-gr-grey text-white rounded-lg px-4 py-2 border border-gr-grey focus:border-gr-red focus:outline-none"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gr-grey mb-2">Current Lap: {currentLap}</label>
              <input
                type="range"
                min={1}
                max={totalLaps}
                value={currentLap}
                onChange={(e) => handleLapChange(parseInt(e.target.value))}
                className="w-full"
              />
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {loading && (
          <div className="text-center py-8">
            <p className="text-gr-grey">Loading replay data...</p>
          </div>
        )}

        {/* Race Timeline */}
        {replayData.length > 0 && !loading && (
          <div className="bg-gr-asphalt rounded-lg p-6 mb-6 border border-gr-grey">
            <h2 className="text-xl font-semibold text-white mb-4">Race Timeline</h2>
            <div className="relative">
              <div className="flex justify-between items-center mb-4">
                {replayData.map((point, idx) => (
                  <div
                    key={idx}
                    className={`flex-1 text-center cursor-pointer ${
                      point.lap === currentLap ? 'scale-110' : ''
                    }`}
                    onClick={() => handleLapChange(point.lap)}
                  >
                    <div className={`w-4 h-4 rounded-full mx-auto mb-2 ${
                      point.lap === currentLap ? 'bg-gr-neon' :
                      point.lap < currentLap ? 'bg-gr-red' : 'bg-gr-grey'
                    }`} />
                    <p className="text-xs text-gr-grey">Lap {point.lap}</p>
                  </div>
                ))}
              </div>
              <div className="h-1 bg-gr-grey rounded-full">
                <div 
                  className="h-1 bg-gr-neon rounded-full transition-all"
                  style={{ width: `${(currentLap / totalLaps) * 100}%` }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Current Lap Analysis */}
        {currentReplayPoint && !loading && (
          <div className="space-y-6">
            {/* Pit Window at Current Lap */}
            {currentReplayPoint.pitWindow && (
              <div className="bg-gr-asphalt rounded-lg p-6 border border-gr-grey">
                <h2 className="text-xl font-semibold text-white mb-4">
                  Pit Window Recommendation (Lap {currentReplayPoint.lap})
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-gr-grey rounded-lg p-4">
                    <p className="text-sm text-gr-grey mb-1">Optimal Pit Lap</p>
                    <p className="text-3xl font-bold text-gr-neon">
                      {currentReplayPoint.pitWindow.optimal_pit_lap}
                    </p>
                  </div>
                  <div className="bg-gr-grey rounded-lg p-4">
                    <p className="text-sm text-gr-grey mb-1">Window</p>
                    <p className="text-xl font-bold text-white">
                      {currentReplayPoint.pitWindow.pit_window_start}-{currentReplayPoint.pitWindow.pit_window_end}
                    </p>
                  </div>
                  <div className="bg-gr-grey rounded-lg p-4">
                    <p className="text-sm text-gr-grey mb-1">Urgency</p>
                    <p className={`text-2xl font-bold ${
                      currentReplayPoint.pitWindow.urgency === 'critical' ? 'text-red-500' :
                      currentReplayPoint.pitWindow.urgency === 'high' ? 'text-orange-500' :
                      currentReplayPoint.pitWindow.urgency === 'medium' ? 'text-yellow-500' :
                      'text-green-500'
                    }`}>
                      {currentReplayPoint.pitWindow.urgency.toUpperCase()}
                    </p>
                  </div>
                  <div className="bg-gr-grey rounded-lg p-4">
                    <p className="text-sm text-gr-grey mb-1">Compound</p>
                    <p className="text-xl font-bold text-gr-neon">
                      {currentReplayPoint.pitWindow.tire_compound_recommendation}
                    </p>
                  </div>
                </div>
                <p className="text-gr-grey text-sm mt-4">{currentReplayPoint.pitWindow.reason}</p>
              </div>
            )}

            {/* Pace Projection at Current Lap */}
            {currentReplayPoint.paceProjection && (
              <div className="bg-gr-asphalt rounded-lg p-6 border border-gr-grey">
                <h2 className="text-xl font-semibold text-white mb-4">
                  Pace Projection (Lap {currentReplayPoint.lap})
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-2 mb-4">
                  {currentReplayPoint.paceProjection.projected_laps.map((proj, idx) => (
                    <div key={idx} className="bg-gr-grey rounded p-3 text-center">
                      <p className="text-xs text-gr-grey">Lap {proj.lap}</p>
                      <p className="text-lg font-bold text-white">{proj.pace.toFixed(2)}s</p>
                    </div>
                  ))}
                </div>
                <div className="mt-4">
                  <p className="text-sm text-gr-grey mb-2">Factors Considered:</p>
                  <div className="flex flex-wrap gap-2">
                    {currentReplayPoint.paceProjection.factors_considered.map((factor, idx) => (
                      <span key={idx} className="px-3 py-1 bg-gr-grey rounded-full text-xs text-white">
                        {factor}
                      </span>
                    ))}
                  </div>
                  <p className="text-sm text-gr-grey mt-3">
                    Confidence: {(currentReplayPoint.paceProjection.confidence * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            )}

            {/* Strategy Evolution Chart */}
            <div className="bg-gr-asphalt rounded-lg p-6 border border-gr-grey">
              <h2 className="text-xl font-semibold text-white mb-4">Pit Window Evolution</h2>
              <div className="space-y-2">
                {replayData.map((point, idx) => {
                  if (!point.pitWindow) return null
                  
                  const isCurrent = point.lap === currentLap
                  const urgencyColors = {
                    critical: 'bg-red-500',
                    high: 'bg-orange-500',
                    medium: 'bg-yellow-500',
                    low: 'bg-green-500'
                  }
                  
                  return (
                    <div
                      key={idx}
                      className={`flex items-center space-x-4 p-3 rounded-lg ${
                        isCurrent ? 'bg-gr-grey border-2 border-gr-neon' : 'bg-gr-grey'
                      }`}
                    >
                      <div className="w-16 text-sm text-gr-grey">Lap {point.lap}</div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <div className={`w-3 h-3 rounded-full ${urgencyColors[point.pitWindow.urgency as keyof typeof urgencyColors] || 'bg-gr-grey'}`} />
                          <span className="text-white font-medium">
                            Optimal: Lap {point.pitWindow.optimal_pit_lap}
                          </span>
                          <span className="text-gr-grey text-sm">
                            (Window: {point.pitWindow.pit_window_start}-{point.pitWindow.pit_window_end})
                          </span>
                        </div>
                      </div>
                      <div className="text-gr-neon font-semibold">
                        {point.pitWindow.tire_compound_recommendation}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        {replayData.length === 0 && !loading && (
          <div className="text-center py-12">
            <p className="text-gr-grey text-lg">Select a driver and load data to view strategy replay</p>
          </div>
        )}
      </main>
    </div>
  )
}

