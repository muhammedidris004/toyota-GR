'use client'

import { useState, useEffect } from 'react'
import Navigation from '../components/Navigation'
import DriverComparisonChart from '../components/DriverComparisonChart'
import { 
  getDataInfo, 
  getTireWear,
  getConsistency,
  getTrafficLoss,
  getPaceDelta,
  type DataInfo,
  type TireWearIndex,
  type DriverConsistencyScore,
  type TrafficLossFactor,
  type PaceDeltaTrend
} from '../../lib/api'

export default function DriverComparison() {
  const [dataInfo, setDataInfo] = useState<DataInfo | null>(null)
  const [selectedDrivers, setSelectedDrivers] = useState<string[]>([])
  const [currentLap, setCurrentLap] = useState(8)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [driverMetrics, setDriverMetrics] = useState<Record<string, {
    tireWear: TireWearIndex | null;
    consistency: DriverConsistencyScore | null;
    traffic: TrafficLossFactor | null;
    pace: PaceDeltaTrend | null;
  }>>({})

  useEffect(() => {
    loadDataInfo()
  }, [])

  const loadDataInfo = async () => {
    try {
      const info = await getDataInfo()
      setDataInfo(info)
      if (info.drivers.length > 0) {
        // Select first 3 drivers by default
        setSelectedDrivers(info.drivers.slice(0, 3))
      }
    } catch (err) {
      console.error('Failed to load data info:', err)
    }
  }

  const loadDriverMetrics = async () => {
    if (selectedDrivers.length === 0) return

    setLoading(true)
    setError(null)
    
    const metrics: Record<string, any> = {}
    
    try {
      await Promise.all(
        selectedDrivers.map(async (driverId) => {
          const [tireWear, consistency, traffic, pace] = await Promise.all([
            getTireWear(driverId, currentLap).catch(() => null),
            getConsistency(driverId).catch(() => null),
            getTrafficLoss(driverId, currentLap).catch(() => null),
            getPaceDelta(driverId).catch(() => null),
          ])
          
          metrics[driverId] = { tireWear, consistency, traffic, pace }
        })
      )
      
      setDriverMetrics(metrics)
    } catch (err: any) {
      setError(err.message || 'Failed to load driver metrics')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (selectedDrivers.length > 0 && dataInfo?.loaded) {
      loadDriverMetrics()
    }
  }, [selectedDrivers, currentLap, dataInfo])

  const toggleDriver = (driverId: string) => {
    setSelectedDrivers(prev => 
      prev.includes(driverId)
        ? prev.filter(d => d !== driverId)
        : [...prev, driverId].slice(0, 5) // Max 5 drivers
    )
  }

  return (
    <div className="min-h-screen bg-gr-black">
      <Navigation />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gr-neon mb-2">Driver Comparison</h1>
          <p className="text-gr-grey">Compare multiple drivers' performance metrics side-by-side</p>
        </div>

        {/* Controls */}
        <div className="bg-gr-asphalt rounded-lg p-6 mb-6 border border-gr-grey">
          <h2 className="text-xl font-semibold text-white mb-4">Comparison Settings</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gr-grey mb-2">Current Lap</label>
              <div className="flex items-center space-x-3">
                <input
                  type="range"
                  value={currentLap}
                  onChange={(e) => setCurrentLap(parseInt(e.target.value) || 1)}
                  min={1}
                  max={dataInfo?.lap_range.max || 100}
                  className="flex-1"
                />
                <input
                  type="number"
                  value={currentLap}
                  onChange={(e) => setCurrentLap(parseInt(e.target.value) || 1)}
                  min={1}
                  max={dataInfo?.lap_range.max || 100}
                  className="w-20 bg-gr-grey text-white rounded-lg px-3 py-2 border border-gr-grey focus:border-gr-red focus:outline-none text-center"
                />
              </div>
              <p className="text-xs text-gr-grey mt-1">
                Lap range: {dataInfo?.lap_range.min || 1} - {dataInfo?.lap_range.max || 100}
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gr-grey mb-2">
                Select Drivers (max 5) - {selectedDrivers.length} selected
              </label>
              <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                {dataInfo?.drivers.map(driverId => (
                  <button
                    key={driverId}
                    onClick={() => toggleDriver(driverId)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      selectedDrivers.includes(driverId)
                        ? 'bg-gr-red text-white shadow-lg shadow-gr-red/50'
                        : 'bg-gr-grey text-gr-grey hover:bg-gr-grey hover:text-white border border-gr-grey'
                    }`}
                  >
                    {driverId}
                  </button>
                ))}
              </div>
              {selectedDrivers.length === 0 && (
                <p className="text-xs text-gr-grey mt-2">Select at least one driver to compare</p>
              )}
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
            <p className="text-gr-grey">Loading driver metrics...</p>
          </div>
        )}

        {/* Comparison Table */}
        {selectedDrivers.length > 0 && !loading && (
          <div className="space-y-6">
            {/* Tire Wear Comparison */}
            <div className="bg-gr-asphalt rounded-lg p-6 border border-gr-grey">
              <h2 className="text-2xl font-semibold text-white mb-4">Tire Wear Index</h2>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[600px]">
                  <thead>
                    <tr className="border-b border-gr-grey">
                      <th className="text-left py-3 px-4 text-gr-grey font-medium">Driver</th>
                      <th className="text-right py-3 px-4 text-gr-grey font-medium">Current TWI</th>
                      <th className="text-right py-3 px-4 text-gr-grey font-medium">Degradation</th>
                      <th className="text-right py-3 px-4 text-gr-grey font-medium">Optimal Pit</th>
                      <th className="text-center py-3 px-4 text-gr-grey font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedDrivers.map(driverId => {
                      const metrics = driverMetrics[driverId]
                      const twi = metrics?.tireWear
                      if (!twi) return null
                      
                      const statusColor = twi.current_twi > 70 ? 'text-red-500' :
                                         twi.current_twi > 50 ? 'text-yellow-500' :
                                         'text-gr-neon'
                      const statusText = twi.current_twi > 70 ? 'Critical' :
                                         twi.current_twi > 50 ? 'High' :
                                         'Good'
                      
                      return (
                        <tr key={driverId} className="border-b border-gr-grey hover:bg-gr-grey transition-colors">
                          <td className="py-4 px-4 text-white font-medium">{driverId}</td>
                          <td className="py-4 px-4 text-right">
                            <div className="flex items-center justify-end space-x-2">
                              <span className={`text-2xl font-bold ${statusColor}`}>
                                {twi.current_twi.toFixed(1)}
                              </span>
                              <div className="w-24 bg-gr-grey rounded-full h-2">
                                <div 
                                  className={`h-2 rounded-full ${
                                    twi.current_twi > 70 ? 'bg-red-500' :
                                    twi.current_twi > 50 ? 'bg-yellow-500' :
                                    'bg-gr-neon'
                                  }`}
                                  style={{ width: `${Math.min(100, twi.current_twi)}%` }}
                                />
                              </div>
                            </div>
                          </td>
                          <td className="py-4 px-4 text-right text-white">
                            {twi.degradation_rate.toFixed(2)} TWI/lap
                          </td>
                          <td className="py-4 px-4 text-right text-gr-red font-semibold">
                            Lap {twi.optimal_pit_lap || 'N/A'}
                          </td>
                          <td className="py-4 px-4 text-center">
                            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                              twi.current_twi > 70 ? 'bg-red-500/20 text-red-400' :
                              twi.current_twi > 50 ? 'bg-yellow-500/20 text-yellow-400' :
                              'bg-gr-neon/20 text-gr-neon'
                            }`}>
                              {statusText}
                            </span>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
              
              {/* Driver Comparison Chart */}
              <div className="mt-6">
                <DriverComparisonChart 
                  data={selectedDrivers.map(driverId => {
                    const metrics = driverMetrics[driverId]
                    const twi = metrics?.tireWear
                    const consistency = metrics?.consistency
                    const traffic = metrics?.traffic
                    return {
                      driver: driverId,
                      tireWear: twi?.current_twi || 0,
                      consistency: consistency?.consistency_score || 0,
                      trafficLoss: traffic?.time_lost_seconds || 0
                    }
                  })}
                />
              </div>
            </div>

            {/* Consistency Comparison */}
            <div className="bg-gr-asphalt rounded-lg p-6 border border-gr-grey">
              <h2 className="text-2xl font-semibold text-white mb-4">Driver Consistency</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {selectedDrivers.map(driverId => {
                  const metrics = driverMetrics[driverId]
                  const consistency = metrics?.consistency
                  if (!consistency) return null
                  
                  const trendColor = consistency.recent_trend === 'improving' ? 'text-gr-neon' :
                                     consistency.recent_trend === 'degrading' ? 'text-red-500' :
                                     'text-white'
                  const trendIcon = consistency.recent_trend === 'improving' ? '↑' :
                                   consistency.recent_trend === 'degrading' ? '↓' :
                                   '→'
                  
                  return (
                    <div key={driverId} className="bg-gr-grey rounded-lg p-5 hover:border border-gr-neon transition-all">
                      <div className="flex justify-between items-start mb-4">
                        <h3 className="text-white font-semibold text-lg">{driverId}</h3>
                        <span className={`text-2xl font-bold ${trendColor}`}>
                          {trendIcon}
                        </span>
                      </div>
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-gr-grey text-sm">Consistency Score</span>
                            <span className="text-2xl font-bold text-gr-neon">
                              {consistency.consistency_score.toFixed(1)}
                            </span>
                          </div>
                          <div className="w-full bg-gr-asphalt rounded-full h-3 overflow-hidden">
                            <div 
                              className="bg-gr-neon h-3 rounded-full transition-all flex items-center justify-end pr-2"
                              style={{ width: `${Math.min(100, consistency.consistency_score)}%` }}
                            >
                              {consistency.consistency_score > 15 && (
                                <span className="text-xs text-gr-black font-bold">
                                  {consistency.consistency_score.toFixed(0)}%
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="pt-2 border-t border-gr-asphalt">
                          <div className="flex justify-between items-center">
                            <span className="text-gr-grey text-sm">Trend</span>
                            <span className={`font-semibold capitalize ${trendColor}`}>
                              {consistency.recent_trend}
                            </span>
                          </div>
                          <div className="flex justify-between items-center mt-1">
                            <span className="text-gr-grey text-sm">Variance</span>
                            <span className="text-white text-sm">
                              {consistency.lap_time_variance.toFixed(3)}s²
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Pace Delta Comparison */}
            <div className="bg-gr-asphalt rounded-lg p-6 border border-gr-grey">
              <h2 className="text-2xl font-semibold text-white mb-4">Pace Delta Trends</h2>
              <div className="space-y-4">
                {selectedDrivers.map(driverId => {
                  const metrics = driverMetrics[driverId]
                  const pace = metrics?.pace
                  if (!pace) return null
                  
                  // Normalize delta values for better visualization
                  const recentDeltas = pace.pace_trend.slice(-10)
                  const maxDelta = Math.max(...recentDeltas.map(Math.abs), 0.1) // Avoid division by zero
                  
                  return (
                    <div key={driverId} className="bg-gr-grey rounded-lg p-5 overflow-hidden">
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="text-white font-semibold text-lg">{driverId}</h3>
                        <div className="text-right">
                          <p className="text-xs text-gr-grey mb-1">Current Delta</p>
                          <p className={`text-2xl font-bold ${
                            pace.current_pace_delta < 0 ? 'text-gr-neon' : 'text-red-500'
                          }`}>
                            {pace.current_pace_delta > 0 ? '+' : ''}{pace.current_pace_delta.toFixed(3)}s
                          </p>
                        </div>
                      </div>
                      
                      {/* Chart Container with proper overflow handling */}
                      <div className="w-full bg-gr-asphalt rounded-lg p-4 mb-3">
                        <div className="flex items-end justify-between space-x-1 h-32 relative">
                          {/* Zero line */}
                          <div className="absolute bottom-0 left-0 right-0 h-px bg-gr-grey opacity-50"></div>
                          
                          {recentDeltas.map((delta, idx) => {
                            // Calculate height as percentage of max delta
                            const heightPercent = Math.max(10, (Math.abs(delta) / maxDelta) * 90)
                            const isPositive = delta >= 0
                            
                            return (
                              <div
                                key={idx}
                                className="flex-1 min-w-[24px] relative group"
                                style={{ height: '100%' }}
                              >
                                <div
                                  className={`w-full rounded-t transition-all ${
                                    isPositive ? 'bg-gr-red' : 'bg-gr-neon'
                                  }`}
                                  style={{
                                    height: `${heightPercent}%`,
                                    marginBottom: isPositive ? '0' : 'auto',
                                    marginTop: isPositive ? 'auto' : '0'
                                  }}
                                >
                                  {/* Tooltip on hover */}
                                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity bg-gr-black text-white text-xs px-2 py-1 rounded whitespace-nowrap z-10 pointer-events-none">
                                    Lap {idx + pace.pace_trend.length - 9}: {delta > 0 ? '+' : ''}{delta.toFixed(2)}s
                                  </div>
                                </div>
                                {/* Lap number label */}
                                <div className="absolute -bottom-5 left-1/2 transform -translate-x-1/2 text-xs text-gr-grey">
                                  {idx + pace.pace_trend.length - 9}
                                </div>
                              </div>
                            )
                          })}
                        </div>
                        
                        {/* Legend */}
                        <div className="flex items-center justify-center space-x-4 mt-8 pt-4 border-t border-gr-grey">
                          <div className="flex items-center space-x-2">
                            <div className="w-4 h-4 bg-gr-neon rounded"></div>
                            <span className="text-xs text-gr-grey">Faster (negative delta)</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div className="w-4 h-4 bg-gr-red rounded"></div>
                            <span className="text-xs text-gr-grey">Slower (positive delta)</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex justify-between items-center pt-3 border-t border-gr-asphalt">
                        <p className="text-sm text-gr-grey">
                          Trend: <span className="text-white capitalize">{pace.trend_direction}</span>
                        </p>
                        <p className="text-sm text-gr-grey">
                          Projected: <span className="text-white">{pace.projected_pace > 0 ? '+' : ''}{pace.projected_pace.toFixed(3)}s</span>
                        </p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Traffic Impact Comparison */}
            <div className="bg-gr-asphalt rounded-lg p-6 border border-gr-grey">
              <h2 className="text-2xl font-semibold text-white mb-4">Traffic Impact</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {selectedDrivers.map(driverId => {
                  const metrics = driverMetrics[driverId]
                  const traffic = metrics?.traffic
                  if (!traffic) return null
                  
                  return (
                    <div key={driverId} className="bg-gr-grey rounded-lg p-5 hover:border border-gr-red transition-all">
                      <div className="flex justify-between items-start mb-4">
                        <h3 className="text-white font-semibold text-lg">{driverId}</h3>
                        {traffic.overtake_opportunity && (
                          <span className="px-2 py-1 bg-gr-neon/20 text-gr-neon text-xs font-semibold rounded">
                            Overtake
                          </span>
                        )}
                      </div>
                      <div className="space-y-3">
                        <div className="bg-gr-asphalt rounded-lg p-3">
                          <div className="flex justify-between items-center mb-1">
                            <span className="text-gr-grey text-sm">Time Lost</span>
                            <span className="text-xl font-bold text-gr-red">
                              +{traffic.traffic_loss.toFixed(2)}s
                            </span>
                          </div>
                          <div className="w-full bg-gr-grey rounded-full h-2 mt-2">
                            <div 
                              className="bg-gr-red h-2 rounded-full"
                              style={{ width: `${Math.min(100, (traffic.traffic_loss / 2.0) * 100)}%` }}
                            />
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          <div className="bg-gr-asphalt rounded-lg p-3 text-center">
                            <p className="text-gr-grey text-xs mb-1">Cars Ahead</p>
                            <p className="text-2xl font-bold text-white">{traffic.cars_ahead}</p>
                          </div>
                          <div className="bg-gr-asphalt rounded-lg p-3 text-center">
                            <p className="text-gr-grey text-xs mb-1">Dirty Air</p>
                            <p className="text-2xl font-bold text-white">
                              {(traffic.dirty_air_factor * 100).toFixed(0)}%
                            </p>
                          </div>
                        </div>
                        <div className="pt-2 border-t border-gr-asphalt">
                          <div className="flex items-center justify-between">
                            <span className="text-gr-grey text-sm">Overtake Opportunity</span>
                            <span className={`font-semibold ${
                              traffic.overtake_opportunity ? 'text-gr-neon' : 'text-gr-grey'
                            }`}>
                              <span className="flex items-center gap-1">
                                {traffic.overtake_opportunity ? (
                                  <>
                                    <svg className="w-4 h-4 text-gr-neon" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                    </svg>
                                    <span>Available</span>
                                  </>
                                ) : (
                                  <>
                                    <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                    </svg>
                                    <span>None</span>
                                  </>
                                )}
                              </span>
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        {selectedDrivers.length === 0 && !loading && (
          <div className="text-center py-12">
            <p className="text-gr-grey text-lg">Select drivers above to compare their performance</p>
          </div>
        )}
      </main>
    </div>
  )
}

