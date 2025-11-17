'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface DriverMetric {
  driver: string
  tireWear: number
  consistency: number
  trafficLoss: number
}

interface DriverComparisonChartProps {
  data: DriverMetric[]
}

export default function DriverComparisonChart({ data }: DriverComparisonChartProps) {
  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2C2C2C" />
          <XAxis 
            dataKey="driver" 
            stroke="#888"
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis 
            stroke="#888"
            domain={[0, 100]}
            label={{ value: 'Score (0-100)', angle: -90, position: 'insideLeft', fill: '#888' }}
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
          <Bar dataKey="tireWear" fill="#E60012" name="Tire Wear Index" />
          <Bar dataKey="consistency" fill="#00FF88" name="Consistency Score" />
          <Bar dataKey="trafficLoss" fill="#888" name="Traffic Loss" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

