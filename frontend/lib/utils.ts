import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function generateId(): string {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

export function detectIntent(query: string): string {
  const lowerQuery = query.toLowerCase();
  
  // Forecast detection
  if (lowerQuery.includes('forecast') || lowerQuery.includes('predict')) {
    return 'forecast';
  }
  
  // Trends detection
  if (lowerQuery.includes('trend') || lowerQuery.includes('trending')) {
    return 'trends';
  }
  
  // Correlation detection
  if (lowerQuery.includes('correlate') || lowerQuery.includes('correlation') || lowerQuery.includes('relate')) {
    return 'correlation';
  }
  
  // Anomaly detection
  if (lowerQuery.includes('anomaly') || lowerQuery.includes('anomalies') || lowerQuery.includes('unusual')) {
    return 'anomalies';
  }
  
  // Default to text query
  return 'text';
}
