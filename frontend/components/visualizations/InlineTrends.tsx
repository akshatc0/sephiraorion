"use client";

import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { TrendsResponse } from '@/lib/types';
import { cn } from '@/lib/utils';

interface InlineTrendsProps {
  data: TrendsResponse;
}

export function InlineTrends({ data }: InlineTrendsProps) {
  const getTrendIcon = (direction: string) => {
    switch (direction.toLowerCase()) {
      case 'increasing':
      case 'upward':
        return <TrendingUp className="size-4" />;
      case 'decreasing':
      case 'downward':
        return <TrendingDown className="size-4" />;
      default:
        return <Minus className="size-4" />;
    }
  };

  const getTrendColor = (direction: string) => {
    switch (direction.toLowerCase()) {
      case 'increasing':
      case 'upward':
        return 'text-green-600 bg-green-50';
      case 'decreasing':
      case 'downward':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="mt-3 bg-white rounded-xl p-3 text-black">
      <h4 className="text-sm font-semibold mb-2">Trend Analysis</h4>
      <div className="space-y-2">
        {data.trends.map((trend, idx) => (
          <div 
            key={idx}
            className="flex items-center justify-between p-2 rounded-lg bg-gray-50"
          >
            <div className="flex items-center gap-2 flex-1">
              <div className={cn(
                "p-1.5 rounded-lg",
                getTrendColor(trend.trend_direction)
              )}>
                {getTrendIcon(trend.trend_direction)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{trend.country}</p>
                <p className="text-xs text-text-secondary capitalize">
                  {trend.trend_direction} • {trend.strength}
                </p>
              </div>
            </div>
            <div className={cn(
              "text-sm font-semibold",
              trend.change_percentage >= 0 ? 'text-green-600' : 'text-red-600'
            )}>
              {trend.change_percentage >= 0 ? '+' : ''}{trend.change_percentage.toFixed(1)}%
            </div>
          </div>
        ))}
      </div>
      <p className="text-xs text-text-secondary mt-3">{data.overall_summary}</p>
    </div>
  );
}
