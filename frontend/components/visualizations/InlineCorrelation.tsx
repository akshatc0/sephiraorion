"use client";

import type { CorrelationResponse } from '@/lib/types';
import { cn } from '@/lib/utils';

interface InlineCorrelationProps {
  data: CorrelationResponse;
}

export function InlineCorrelation({ data }: InlineCorrelationProps) {
  const countries = Object.keys(data.correlation_matrix);
  
  const getCorrelationColor = (value: number) => {
    if (value >= 0.7) return 'bg-green-500 text-white';
    if (value >= 0.4) return 'bg-green-300 text-black';
    if (value >= 0) return 'bg-gray-200 text-black';
    if (value >= -0.4) return 'bg-red-200 text-black';
    return 'bg-red-500 text-white';
  };

  return (
    <div className="mt-3 bg-white rounded-xl p-3 text-black">
      <h4 className="text-sm font-semibold mb-2">Correlation Matrix</h4>
      
      {/* Matrix */}
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr>
              <th className="p-1"></th>
              {countries.map((country) => (
                <th key={country} className="p-1 text-center">
                  <div className="rotate-[-45deg] origin-center whitespace-nowrap text-[10px]">
                    {country.slice(0, 3).toUpperCase()}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {countries.map((row) => (
              <tr key={row}>
                <td className="p-1 font-medium text-[10px] whitespace-nowrap">
                  {row.slice(0, 10)}
                </td>
                {countries.map((col) => {
                  const value = data.correlation_matrix[row][col];
                  return (
                    <td key={col} className="p-0.5">
                      <div
                        className={cn(
                          "size-6 flex items-center justify-center rounded text-[9px] font-semibold",
                          getCorrelationColor(value)
                        )}
                        title={`${row} vs ${col}: ${value.toFixed(2)}`}
                      >
                        {value.toFixed(1)}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Significant Correlations */}
      {data.significant_correlations && data.significant_correlations.length > 0 && (
        <div className="mt-3">
          <p className="text-xs font-semibold mb-1">Key Correlations:</p>
          <div className="space-y-1">
            {data.significant_correlations.slice(0, 3).map((corr, idx) => (
              <div key={idx} className="text-xs flex items-center justify-between bg-gray-50 p-1.5 rounded">
                <span className="text-text-secondary">
                  {corr.country1} ↔ {corr.country2}
                </span>
                <span className="font-semibold">
                  {corr.correlation.toFixed(2)} ({corr.strength})
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <p className="text-xs text-text-secondary mt-2">{data.summary}</p>
    </div>
  );
}
