"use client";

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { useStore } from "@/lib/store";
import { chatAPI } from "@/lib/api";
import { generateId, detectIntent } from "@/lib/utils";
import type { Message } from "@/lib/types";
import { ChatInput } from "./ChatInput";
import { MessageBubble } from "./MessageBubble";
import { AnimatedBackground } from "./AnimatedBackground";

export function ChatInterface() {
  const { messages, addMessage, updateLastMessage, isLoading, setLoading, selectedCountries } = useStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const conversationHistory = useRef<Array<{ role: string; content: string }>>([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (messageText: string) => {
    if (!messageText.trim() || isLoading) return;

    setIsSubmitting(true);
    setLoading(true);

    // Add user message
    const userMessage: Message = {
      id: generateId(),
      sentByMe: true,
      type: 'text',
      message: messageText,
      timestamp: new Date(),
    };
    addMessage(userMessage);

    // Add to conversation history
    conversationHistory.current.push({
      role: 'user',
      content: messageText,
    });

    // Add loading message
    const loadingMessage: Message = {
      id: generateId(),
      sentByMe: false,
      type: 'loading',
      message: '',
      timestamp: new Date(),
    };
    addMessage(loadingMessage);

    try {
      // Detect intent to determine if we need predictions
      const intents = detectIntent(messageText);
      
      // Send chat request
      const chatResponse = await chatAPI.sendMessage({
        query: messageText,
        conversation_history: conversationHistory.current.slice(-10), // Keep last 10 messages
      });

      // Add assistant response to history
      conversationHistory.current.push({
        role: 'assistant',
        content: chatResponse.response,
      });

      // Check if we should fetch predictions based on intent
      let visualizationData = null;
      let visualizationType: Message['type'] = 'text';

      // If user asked for forecast
      if (intents.includes('forecast')) {
        try {
          const forecastResponse = await chatAPI.getForecast({
            country: selectedCountries[0] || 'United States',
            days: 30,
            confidence_level: 0.95,
          });
          visualizationData = forecastResponse;
          visualizationType = 'forecast';
        } catch (e) {
          console.error('Forecast error:', e);
        }
      }
      // If user asked for trends
      else if (intents.includes('trends')) {
        try {
          const trendsResponse = await chatAPI.getTrends({
            countries: selectedCountries.slice(0, 5),
            days: 90,
          });
          visualizationData = trendsResponse;
          visualizationType = 'trends';
        } catch (e) {
          console.error('Trends error:', e);
        }
      }
      // If user asked for correlations
      else if (intents.includes('correlation')) {
        try {
          const correlationResponse = await chatAPI.getCorrelations({
            countries: selectedCountries.slice(0, 5),
            days: 90,
          });
          visualizationData = correlationResponse;
          visualizationType = 'correlation';
        } catch (e) {
          console.error('Correlation error:', e);
        }
      }
      // If user asked for anomalies
      else if (intents.includes('anomalies')) {
        try {
          const anomalyResponse = await chatAPI.getAnomalies({
            countries: selectedCountries,
            threshold: 2.0,
          });
          visualizationData = anomalyResponse;
          visualizationType = 'anomalies';
        } catch (e) {
          console.error('Anomaly error:', e);
        }
      }

      // Update the loading message with actual response
      updateLastMessage({
        type: visualizationType,
        message: chatResponse.response,
        data: visualizationData || { sources: chatResponse.sources },
      });

    } catch (error: any) {
      console.error('Chat error:', error);
      
      // Update loading message with error
      updateLastMessage({
        type: 'error',
        message: error.message || 'Failed to get response. Please try again.',
      });
    } finally {
      setLoading(false);
      setTimeout(() => setIsSubmitting(false), 500);
    }
  };

  return (
    <div className="relative h-screen w-screen overflow-hidden bg-background font-medium text-black">
      {/* Animated gradient background */}
      <AnimatedBackground isSubmitting={isSubmitting} />

      {/* Main content container */}
      <div className="relative z-10 h-full w-full flex flex-col">
        {/* Header - Fixed at top */}
        <div className="text-center py-6 px-4 shrink-0">
          <h1 className="text-2xl md:text-3xl font-bold mb-1">Sephira Orion</h1>
          <p className="text-sm md:text-base text-text-secondary">
            AI-Powered Global Sentiment Intelligence
          </p>
        </div>

        {/* Messages area - Scrollable middle section */}
        <div className="flex-1 overflow-y-auto px-4 pb-4 min-h-0">
          <div className="flex flex-col justify-end min-h-full gap-3 max-w-4xl mx-auto">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-text-secondary mb-4">
                  Welcome! Ask me anything about global sentiment data.
                </p>
                <div className="flex flex-wrap gap-2 justify-center">
                  <SuggestionChip 
                    text="Forecast Russia for 30 days"
                    onClick={() => handleSendMessage("Forecast Russia for 30 days")}
                  />
                  <SuggestionChip 
                    text="Show me trends in Asia"
                    onClick={() => handleSendMessage("Show me trends in Asia")}
                  />
                  <SuggestionChip 
                    text="Detect any anomalies"
                    onClick={() => handleSendMessage("Detect any anomalies recently")}
                  />
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input area - Fixed at bottom */}
        <div className="flex justify-center px-4 py-6 shrink-0 border-t border-gray-200/50">
          <ChatInput 
            onSubmit={handleSendMessage} 
            disabled={isLoading}
          />
        </div>
      </div>
    </div>
  );
}

function SuggestionChip({ text, onClick }: { text: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="px-4 py-2 bg-white text-sm rounded-full shadow-soft hover:shadow-medium transition-all hover:scale-105"
    >
      {text}
    </button>
  );
}
