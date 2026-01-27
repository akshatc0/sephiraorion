"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { Message } from "@/lib/types";
import { LoadingDots } from "@/components/ui/LoadingDots";
import { MarkdownContent } from "@/components/ui/MarkdownContent";
import dynamic from "next/dynamic";

// Lazy load visualization components
const InlineForecast = dynamic(() => import("@/components/visualizations/InlineForecast").then(mod => ({ default: mod.InlineForecast })), { ssr: false });
const InlineTrends = dynamic(() => import("@/components/visualizations/InlineTrends").then(mod => ({ default: mod.InlineTrends })), { ssr: false });
const InlineCorrelation = dynamic(() => import("@/components/visualizations/InlineCorrelation").then(mod => ({ default: mod.InlineCorrelation })), { ssr: false });
const InlineAnomalies = dynamic(() => import("@/components/visualizations/InlineAnomalies").then(mod => ({ default: mod.InlineAnomalies })), { ssr: false });

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const renderVisualization = () => {
    if (!message.data) return null;

    switch (message.type) {
      case 'forecast':
        return <InlineForecast data={message.data} />;
      case 'trends':
        return <InlineTrends data={message.data} />;
      case 'correlation':
        return <InlineCorrelation data={message.data} />;
      case 'anomalies':
        return <InlineAnomalies data={message.data} />;
      default:
        return null;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, type: "spring", bounce: 0.4 }}
      className={cn([
        "max-w-[80%] md:max-w-[600px]",
        "break-words px-[14px] py-[10px]",
        "overflow-hidden text-sm rounded-card",
        message.sentByMe
          ? "self-end bg-white text-black shadow-medium"
          : "self-start card-gradient text-white shadow-medium",
      ])}
    >
      {message.type === 'loading' ? (
        <LoadingDots />
      ) : message.type === 'error' ? (
        <div className="text-red-400">
          <p className="font-semibold">Error</p>
          <p className="will-change-transform">{message.message}</p>
        </div>
      ) : (
        <>
          <MarkdownContent content={message.message} className="will-change-transform" />
          {renderVisualization()}
          {message.data?.sources && message.data.sources.length > 0 && !message.sentByMe && (
            <div className="mt-2 pt-2 border-t border-white/20">
              <p className="text-xs text-text-secondary">
                Sources: {message.data.sources.slice(0, 3).map((s: any) => s.country).join(", ")}
                {message.data.sources.length > 3 && ` +${message.data.sources.length - 3} more`}
              </p>
            </div>
          )}
        </>
      )}
    </motion.div>
  );
}
