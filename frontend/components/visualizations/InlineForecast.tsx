"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import type { ForecastResponse } from '@/lib/types';

interface InlineForecastProps {
  data: ForecastResponse;
}

export function InlineForecast({ data }: InlineForecastProps) {
  const chartData = data.forecasts.map(f => ({
    date: new Date(f.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    predicted: f.predicted_sentiment,
    lower: f.lower_bound,
    upper: f.upper_bound,
  }));

  return (
    <div className="mt-3 bg-white rounded-xl p-3 text-black">
      <h4 className="text-sm font-semibold mb-2">{data.country} Forecast</h4>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 11, fill: '#6b7280' }}
          />
          <YAxis 
            tick={{ fontSize: 11, fill: '#6b7280' }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#fff', 
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              fontSize: '12px'
            }}
          />
          <Legend 
            wrapperStyle={{ fontSize: '11px' }}
          />
          <Area
            type="monotone"
            dataKey="upper"
            stackId="1"
            stroke="none"
            fill="rgba(14, 165, 233, 0.1)"
            name="Upper Bound"
          />
          <Area
            type="monotone"
            dataKey="lower"
            stackId="1"
            stroke="none"
            fill="rgba(14, 165, 233, 0.1)"
            name="Lower Bound"
          />
          <Line
            type="monotone"
            dataKey="predicted"
            stroke="#0ea5e9"
            strokeWidth={2}
            dot={{ r: 3 }}
            name="Predicted"
          />
        </AreaChart>
      </ResponsiveContainer>
      <p className="text-xs text-text-secondary mt-2">{data.summary}</p>
    </div>
  );
}
