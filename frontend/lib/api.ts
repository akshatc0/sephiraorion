import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000, // Increased to 60 seconds for GPT-5.1 and web search
});

export interface ChatRequest {
  query: string;
  conversation_history?: Array<{ role: string; content: string }>;
}

export interface ChatResponse {
  response: string;
  context_used: boolean;
  sources?: string[];
  query_type?: string;
}

export interface ForecastRequest {
  country: string;
  periods?: number;
}

export interface TrendRequest {
  country?: string;
  start_date?: string;
  end_date?: string;
}

export interface CorrelationRequest {
  country1: string;
  country2: string;
  start_date?: string;
  end_date?: string;
}

export interface AnomalyRequest {
  country?: string;
  threshold?: number;
}

export const chatAPI = {
  sendMessage: async (data: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post('/api/chat', data);
    return response.data;
  },

  getForecast: async (data: ForecastRequest) => {
    const response = await api.post('/api/predict/forecast', data);
    return response.data;
  },

  getTrends: async (data: TrendRequest) => {
    const response = await api.post('/api/predict/trends', data);
    return response.data;
  },

  getCorrelations: async (data: CorrelationRequest) => {
    const response = await api.post('/api/predict/correlation', data);
    return response.data;
  },

  getAnomalies: async (data: AnomalyRequest) => {
    const response = await api.post('/api/predict/anomalies', data);
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/api/data/stats');
    return response.data;
  },

  health: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },
};

export default api;
