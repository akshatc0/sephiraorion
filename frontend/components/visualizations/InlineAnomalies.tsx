"use client";

import { AlertTriangle, AlertCircle, Info } from 'lucide-react';
import type { AnomalyResponse } from '@/lib/types';
import { cn } from '@/lib/utils';

interface InlineAnomaliesProps {
  data: AnomalyResponse;
}

export function InlineAnomalies({ data }: InlineAnomaliesProps) {
  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
      case 'severe':
        return <AlertTriangle className="size-4" />;
      case 'medium':
      case 'moderate':
        return <AlertCircle className="size-4" />;
      default:
        return <Info className="size-4" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
      case 'severe':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'medium':
      case 'moderate':
        return 'text-orange-600 bg-orange-50 border-orange-200';
      default:
        return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  return (
    <div className="mt-3 bg-white rounded-xl p-3 text-black">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-semibold">Detected Anomalies</h4>
        <span className="text-xs bg-gray-100 px-2 py-0.5 rounded-full">
          {data.count} found
        </span>
      </div>
      
      {data.anomalies.length === 0 ? (
        <p className="text-sm text-text-secondary">No anomalies detected.</p>
      ) : (
        <div className="space-y-2">
          {data.anomalies.slice(0, 5).map((anomaly, idx) => (
            <div 
              key={idx}
              className={cn(
                "p-2.5 rounded-lg border",
                getSeverityColor(anomaly.severity)
              )}
            >
              <div className="flex items-start gap-2">
                <div className="mt-0.5">
                  {getSeverityIcon(anomaly.severity)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <p className="text-sm font-semibold">{anomaly.country}</p>
                    <span className="text-xs opacity-70">
                      {new Date(anomaly.date).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-xs mb-1">{anomaly.description}</p>
                  <div className="flex items-center gap-3 text-xs opacity-70">
                    <span>Value: {anomaly.sentiment.toFixed(2)}</span>
                    <span>
                      Expected: {anomaly.expected_range[0].toFixed(2)} - {anomaly.expected_range[1].toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
          {data.anomalies.length > 5 && (
            <p className="text-xs text-center text-text-secondary">
              +{data.anomalies.length - 5} more anomalies
            </p>
          )}
        </div>
      )}
      
      <p className="text-xs text-text-secondary mt-3">{data.analysis}</p>
    </div>
  );
}
