'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface TireWearDataPoint {
  lap: number
  twi: number
  degradationRate: number
}

interface TireWearChartProps {
  data: TireWearDataPoint[]
  currentLap: number
}

export default function TireWearChart({ data, currentLap }: TireWearChartProps) {
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
            label={{ value: 'Tire Wear Index', angle: -90, position: 'insideLeft', fill: '#888' }}
            domain={[0, 100]}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1a1a1a', 
              border: '1px solid #2C2C2C',
              borderRadius: '8px',
              color: '#fff'
            }}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="twi" 
            stroke="#E60012" 
            strokeWidth={2}
            name="Tire Wear Index"
            dot={{ fill: '#E60012', r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line 
            type="monotone" 
            dataKey="degradationRate" 
            stroke="#00FF88" 
            strokeWidth={2}
            name="Degradation Rate"
            dot={{ fill: '#00FF88', r: 4 }}
            strokeDasharray="5 5"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

