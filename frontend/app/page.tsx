'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import Navigation from './components/Navigation'
import CaseStudyPanel from './components/CaseStudyPanel'
import { getDataInfo, listTRDTracks, loadTRDData, type DataInfo } from '../lib/api'

export default function Home() {
  const router = useRouter()
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'error'>('checking')
  const [dataInfo, setDataInfo] = useState<DataInfo | null>(null)
  const [tracks, setTracks] = useState<string[]>([])
  const [demoLoading, setDemoLoading] = useState(false)

  // Check backend connection on mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://toyota-gr.onrender.com'}/health`)
        if (response.ok) {
          setBackendStatus('connected')
          // Load data info if backend is connected
          try {
            const info = await getDataInfo()
            setDataInfo(info)
          } catch (err) {
            console.error('Failed to load data info:', err)
          }
          // Load tracks
          try {
            const tracksRes = await listTRDTracks()
            setTracks(tracksRes.tracks || [])
          } catch (err) {
            console.error('Failed to load tracks:', err)
          }
        } else {
          setBackendStatus('error')
        }
      } catch (error) {
        setBackendStatus('error')
      }
    }

    checkBackend()
  }, [])

  // One-Click Demo Scenario Handler
  // This loads COTA Race 1 data and navigates to console with pre-filled params
  const handleRunDemo = async () => {
    if (backendStatus !== 'connected') return
    
    setDemoLoading(true)
    try {
      // Step 1: Load COTA Race 1 data
      await loadTRDData('COTA', 'Race 1')
      
      // Step 2: Get data info to find a driver
      const info = await getDataInfo()
      const demoDriver = info.drivers.length > 0 ? info.drivers[0] : 'DRIVER_01'
      const demoLap = Math.floor((info.lap_range.min + info.lap_range.max) / 2) || 8
      
      // Step 3: Navigate to console with query params for auto-loading
      router.push(`/console?demo=true&track=COTA&race=Race%201&driver=${encodeURIComponent(demoDriver)}&lap=${demoLap}`)
    } catch (err: any) {
      console.error('Demo failed:', err)
      alert('Failed to load demo scenario. Please try manually loading data.')
      setDemoLoading(false)
    }
  }

  // Show loading state while checking backend
  if (backendStatus === 'checking') {
    return (
      <div className="min-h-screen bg-gr-black flex items-center justify-center">
        <div className="text-center animate-fade-in">
          <div className="text-6xl font-bold bg-gradient-to-r from-gr-red to-gr-neon bg-clip-text text-transparent mb-4 animate-pulse-slow">
            GR
          </div>
          <div className="text-white text-lg">Initializing Race Strategist AI...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gr-black">
      <Navigation />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16 animate-slide-up">
          <div className="inline-block mb-6">
            <div className="text-7xl font-bold bg-gradient-to-r from-gr-red via-gr-neon to-gr-red bg-clip-text text-transparent mb-4 animate-glow">
              GR Race Strategist AI
            </div>
          </div>
          <p className="text-3xl font-light text-white/90 mb-4">
            Enterprise-Grade Race Strategy & Performance Analytics
          </p>
          <p className="text-lg text-gr-grey max-w-2xl mx-auto">
            Real-time pit-window optimization, tire-wear prediction, and strategic decision-making for professional racing teams
          </p>
        </div>
        
        {/* Backend Status Indicator */}
        <div className="mb-12 text-center animate-fade-in">
          <div className={`inline-flex items-center gap-3 px-6 py-3 rounded-xl font-semibold transition-all ${
            backendStatus === 'connected' 
              ? 'bg-gradient-to-r from-gr-neon to-gr-neon-dark text-gr-black shadow-gr-neon' 
              : backendStatus === 'checking'
              ? 'bg-gr-grey text-white'
              : backendStatus === 'error'
              ? 'bg-gr-red text-white shadow-gr-red'
              : 'bg-gr-grey text-white'
          }`}>
            <span className={`w-2 h-2 rounded-full bg-current ${
              backendStatus === 'connected' ? 'animate-pulse' : ''
            }`}></span>
            {backendStatus === 'connected' && (
              <>
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>System Operational</span>
              </>
            )}
            {backendStatus === 'checking' && 'Initializing...'}
            {backendStatus === 'error' && (
              <>
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span>Connection Error</span>
              </>
            )}
          </div>
          {backendStatus === 'error' && (
            <p className="text-sm text-gr-grey mt-4">
              Ensure backend is running on https://toyota-gr.onrender.com
            </p>
          )}
        </div>

        {/* One-Click Demo Scenario Button */}
        {backendStatus === 'connected' && (
          <div className="mb-12 text-center animate-slide-up">
            <button
              onClick={handleRunDemo}
              disabled={demoLoading}
              className="btn-primary text-lg px-8 py-4 disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden group"
            >
              {demoLoading ? (
                <span className="flex items-center gap-3">
                  <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                  <span>Loading Demo Scenario...</span>
                </span>
              ) : (
                <>
                  <span className="relative z-10 flex items-center gap-3">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="font-bold">Run GR Cup Demo Scenario</span>
                  </span>
                  <span className="absolute inset-0 bg-gradient-to-r from-gr-red via-gr-neon to-gr-red opacity-0 group-hover:opacity-20 transition-opacity"></span>
                </>
              )}
            </button>
            <p className="text-sm text-gr-grey mt-4">
              Instantly load COTA Race 1 data and see the strategy engine in action
            </p>
          </div>
        )}

        {/* Feature 4: Case Study Panel - Real Data Insight */}
        <CaseStudyPanel />

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <Link 
            href="/console" 
            className="card group p-8 hover:scale-105 transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="w-12 h-12 rounded-lg bg-gr-red/20 flex items-center justify-center group-hover:bg-gr-red/40 transition-colors">
                <svg className="w-6 h-6 text-gr-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="w-10 h-10 rounded-full bg-gr-red/20 flex items-center justify-center group-hover:bg-gr-red/40 transition-colors">
                <span className="text-gr-red">→</span>
              </div>
            </div>
            <h2 className="text-2xl font-bold text-white mb-3 group-hover:text-gr-neon transition-colors">
              Race Engineer Console
            </h2>
            <p className="text-gr-grey leading-relaxed">
              Real-time dashboard with live race metrics, tire wear analysis, and AI-powered strategy recommendations
            </p>
            <div className="mt-6 pt-6 border-t border-gr-grey/30">
              <div className="flex items-center text-sm text-gr-neon">
                <span>Explore Console</span>
                <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </div>
          </Link>

          <Link 
            href="/comparison" 
            className="card group p-8 hover:scale-105 transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="w-12 h-12 rounded-lg bg-gr-neon/20 flex items-center justify-center group-hover:bg-gr-neon/40 transition-colors">
                <svg className="w-6 h-6 text-gr-neon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div className="w-10 h-10 rounded-full bg-gr-neon/20 flex items-center justify-center group-hover:bg-gr-neon/40 transition-colors">
                <span className="text-gr-neon">→</span>
              </div>
            </div>
            <h2 className="text-2xl font-bold text-white mb-3 group-hover:text-gr-neon transition-colors">
              Driver Comparison
            </h2>
            <p className="text-gr-grey leading-relaxed">
              Compare multiple drivers' performance, tire wear, consistency, and pace projections with advanced analytics
            </p>
            <div className="mt-6 pt-6 border-t border-gr-grey/30">
              <div className="flex items-center text-sm text-gr-neon">
                <span>Compare Drivers</span>
                <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </div>
          </Link>

          <Link 
            href="/replay" 
            className="card group p-8 hover:scale-105 transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="w-12 h-12 rounded-lg bg-gr-red/20 flex items-center justify-center group-hover:bg-gr-red/40 transition-colors">
                <svg className="w-6 h-6 text-gr-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="w-10 h-10 rounded-full bg-gr-red/20 flex items-center justify-center group-hover:bg-gr-red/40 transition-colors">
                <span className="text-gr-red">→</span>
              </div>
            </div>
            <h2 className="text-2xl font-bold text-white mb-3 group-hover:text-gr-neon transition-colors">
              Strategy Replay
            </h2>
            <p className="text-gr-grey leading-relaxed">
              Review and analyze past race strategies with timeline visualizations and post-race performance insights
            </p>
            <div className="mt-6 pt-6 border-t border-gr-grey/30">
              <div className="flex items-center text-sm text-gr-neon">
                <span>View Replay</span>
                <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </div>
          </Link>
        </div>

        {/* Data Status */}
        {dataInfo && (
          <div className="card p-8 mb-12 animate-slide-up">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">System Status</h2>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-gr-neon animate-pulse"></span>
                <span className="text-sm text-gr-grey">Live</span>
              </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="metric-card">
                <p className="text-xs uppercase tracking-wider text-gr-grey mb-2">Data Status</p>
                <p className="text-2xl font-bold text-gr-neon">
                  {dataInfo.loaded ? 'Active' : 'Standby'}
                </p>
              </div>
              <div className="metric-card">
                <p className="text-xs uppercase tracking-wider text-gr-grey mb-2">Drivers</p>
                <p className="text-2xl font-bold text-white">{dataInfo.drivers.length}</p>
              </div>
              <div className="metric-card">
                <p className="text-xs uppercase tracking-wider text-gr-grey mb-2">Lap Range</p>
                <p className="text-2xl font-bold text-white">
                  {dataInfo.lap_range.min}-{dataInfo.lap_range.max}
                </p>
              </div>
              <div className="metric-card">
                <p className="text-xs uppercase tracking-wider text-gr-grey mb-2">Total Laps</p>
                <p className="text-2xl font-bold text-white">{dataInfo.total_laps}</p>
              </div>
            </div>
          </div>
        )}

        {/* Available Tracks */}
        {tracks.length > 0 && (
          <div className="card p-8 animate-slide-up">
            <h2 className="text-2xl font-bold text-white mb-6">Available Tracks</h2>
            <div className="flex flex-wrap gap-3">
              {tracks.map((track) => (
                <div
                  key={track}
                  className="px-4 py-2 bg-gr-grey/30 border border-gr-grey/50 rounded-lg text-sm font-medium text-white hover:border-gr-neon hover:bg-gr-neon/10 transition-all cursor-default"
                >
                  {track}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-16 pt-8 border-t border-gr-grey/30 text-center">
          <p className="text-gr-grey text-sm">
            Built for Toyota GR "Hack the Track" Devpost Hackathon
          </p>
          <p className="text-gr-grey text-xs mt-2">
            Enterprise-grade race strategy analytics platform
          </p>
        </div>
      </main>
    </div>
  )
}
