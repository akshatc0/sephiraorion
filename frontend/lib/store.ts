import { create } from 'zustand';
import type { Message } from './types';

interface ChatStore {
  messages: Message[];
  isLoading: boolean;
  selectedCountries: string[];
  addMessage: (message: Message) => void;
  updateLastMessage: (updates: Partial<Omit<Message, 'id' | 'sentByMe' | 'timestamp'>>) => void;
  setLoading: (loading: boolean) => void;
  setSelectedCountries: (countries: string[]) => void;
  clearMessages: () => void;
}

export const useStore = create<ChatStore>((set) => ({
  messages: [],
  isLoading: false,
  selectedCountries: ['United States'],
  
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),
  
  updateLastMessage: (updates) =>
    set((state) => ({
      messages: state.messages.map((msg, idx) =>
        idx === state.messages.length - 1
          ? { ...msg, ...updates }
          : msg
      ),
    })),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  setSelectedCountries: (countries) => set({ selectedCountries: countries }),
  
  clearMessages: () => set({ messages: [] }),
}));
