export type MessageType = 
  | 'text'
  | 'forecast'
  | 'trends'
  | 'correlation'
  | 'anomalies'
  | 'error'
  | 'loading';

export interface Message {
  id: string;
  sentByMe: boolean;
  type: MessageType;
  message: string;
  data?: any;
  timestamp: Date;
}

export interface ChatRequest {
  query: string;
  conversation_history?: Array<{ role: string; content: string }>;
}

export interface ChatResponse {
  response: string;
  sources: Array<{
    country: string;
    date: string;
    sentiment: number;
    chunk_id: string;
  }>;
  context_used?: string;
}

export interface ForecastRequest {
  country: string;
  days: number;
  confidence_level: number;
}

export interface ForecastResponse {
  country: string;
  forecast_period: {
    start_date: string;
    end_date: string;
  };
  forecasts: Array<{
    date: string;
    predicted_sentiment: number;
    lower_bound: number;
    upper_bound: number;
  }>;
  summary: string;
}

export interface TrendsRequest {
  countries: string[];
  days: number;
}

export interface TrendsResponse {
  analysis_period: {
    start_date: string;
    end_date: string;
  };
  trends: Array<{
    country: string;
    trend_direction: string;
    strength: string;
    change_percentage: number;
    summary: string;
  }>;
  overall_summary: string;
}

export interface CorrelationRequest {
  countries: string[];
  days?: number;
}

export interface CorrelationResponse {
  correlation_matrix: Record<string, Record<string, number>>;
  summary: string;
  significant_correlations: Array<{
    country1: string;
    country2: string;
    correlation: number;
    strength: string;
  }>;
}

export interface AnomalyRequest {
  countries: string[];
  threshold: number;
}

export interface AnomalyResponse {
  anomalies: Array<{
    country: string;
    date: string;
    sentiment: number;
    expected_range: [number, number];
    severity: string;
    description: string;
  }>;
  count: number;
  countries_analyzed: number;
  analysis: string;
}
