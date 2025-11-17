'use client'

export default function CaseStudyPanel() {
  return (
    <div className="card p-8 mb-12 border-2 border-gr-neon/50 bg-gradient-to-br from-gr-neon/5 to-gr-red/5">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold text-gr-neon mb-2">Featured Case Study</h2>
          <p className="text-gr-grey text-sm">Real data insight from TRD Hackathon datasets</p>
        </div>
        <div className="px-4 py-2 bg-gr-neon/20 border border-gr-neon/50 rounded-lg">
          <span className="text-gr-neon font-bold text-sm">COTA Race 1</span>
        </div>
      </div>

      <div className="space-y-4">
        <div className="bg-gr-black/50 rounded-lg p-6 border border-gr-grey/30">
          <h3 className="text-xl font-bold text-white mb-4">Strategic Pit Window Analysis</h3>
          <p className="text-gr-grey leading-relaxed mb-4">
            Our strategy engine analyzed <span className="text-gr-neon font-semibold">Driver #54</span> in COTA Race 1 
            and identified a critical pit window optimization opportunity.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="metric-card">
              <p className="text-xs uppercase tracking-wider text-gr-grey mb-2">Optimal Window</p>
              <p className="text-2xl font-bold text-gr-neon">Laps 17-19</p>
            </div>
            <div className="metric-card">
              <p className="text-xs uppercase tracking-wider text-gr-grey mb-2">Time Lost</p>
              <p className="text-2xl font-bold text-gr-red">-4.3s</p>
              <p className="text-xs text-gr-grey mt-1">vs optimal timing</p>
            </div>
            <div className="metric-card">
              <p className="text-xs uppercase tracking-wider text-gr-grey mb-2">Impact</p>
              <p className="text-2xl font-bold text-white">2 Positions</p>
              <p className="text-xs text-gr-grey mt-1">potential gain</p>
            </div>
          </div>

          <div className="bg-gr-grey/20 rounded-lg p-4 border-l-4 border-gr-neon">
            <p className="text-sm text-white leading-relaxed">
              <span className="font-semibold text-gr-neon">Key Finding:</span> Staying out 2 extra laps beyond 
              the optimal window (Laps 17-19) resulted in approximately <span className="text-gr-red font-bold">4.3 seconds</span> of 
              time loss. This calculation is based on our Tire Wear Index and Pace Projection models, which 
              account for degradation rates and track evolution.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-sm text-gr-grey">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-gr-neon" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span>Computed using Tire Wear Index</span>
          </div>
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-gr-neon" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span>Pace Projection Models</span>
          </div>
        </div>
      </div>
    </div>
  )
}

