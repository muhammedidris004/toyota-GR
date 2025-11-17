'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts'

interface PaceDataPoint {
  lap: number
  projectedPace: number
  currentPace?: number
}

interface PaceProjectionChartProps {
  data: PaceDataPoint[]
  currentLap: number
}

export default function PaceProjectionChart({ data, currentLap }: PaceProjectionChartProps) {
  // Format pace for display (seconds to MM:SS.mmm)
  const formatPace = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = (seconds % 60).toFixed(3)
    return `${mins}:${secs.padStart(6, '0')}`
  }

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2C2C2C" />
          <XAxis 
            dataKey="lap" 
            stroke="#888"
            label={{ value: 'Lap Number', position: 'insideBottom', offset: -5, fill: '#888' }}
          />
          <YAxis 
            stroke="#888"
            label={{ value: 'Lap Time (seconds)', angle: -90, position: 'insideLeft', fill: '#888' }}
            tickFormatter={(value) => value.toFixed(1)}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1a1a1a', 
              border: '1px solid #2C2C2C',
              borderRadius: '8px',
              color: '#fff'
            }}
            formatter={(value: number) => formatPace(value)}
          />
          <Legend />
          <ReferenceLine 
            x={currentLap} 
            stroke="#00FF88" 
            strokeDasharray="3 3"
            label={{ value: 'Current Lap', position: 'top', fill: '#00FF88' }}
          />
          <Line 
            type="monotone" 
            dataKey="projectedPace" 
            stroke="#E60012" 
            strokeWidth={2}
            name="Projected Pace"
            dot={{ fill: '#E60012', r: 4 }}
            activeDot={{ r: 6 }}
          />
          {data.some(d => d.currentPace) && (
            <Line 
              type="monotone" 
              dataKey="currentPace" 
              stroke="#888" 
              strokeWidth={1}
              name="Current Pace"
              dot={{ fill: '#888', r: 3 }}
              strokeDasharray="5 5"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

