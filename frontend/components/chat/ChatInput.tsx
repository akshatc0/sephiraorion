"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ArrowUp, Plus } from "lucide-react";
import React, { useState } from "react";
import useSound from "use-sound";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSubmit: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSubmit, disabled = false }: ChatInputProps) {
  const [inputValue, setInputValue] = useState("");
  const [arrow, setArrow] = useState(true);
  
  // Sound effect (optional - will work if audio file exists)
  const [play] = useSound("/audio/send2.wav", {
    volume: 0.2,
  });

  const handleSubmit = () => {
    if (!inputValue.trim() || disabled) return;
    
    // Play sound (will fail silently if file doesn't exist)
    try {
      play();
    } catch (e) {
      // Silently fail if audio not available
    }
    
    setArrow(false);
    onSubmit(inputValue.trim());
    setInputValue("");
    
    // Reset arrow animation
    setTimeout(() => setArrow(true), 100);
  };

  return (
    <div className="relative w-full max-w-lg">
      <div className="relative rounded-3xl bg-white p-1 shadow-soft">
        <div className="relative flex items-center justify-between rounded-3xl border-gray-100 bg-white p-1.5 z-20">
          {/* Main input field */}
          <div className="flex flex-1 items-center gap-3 pr-3">
            <button 
              className="flex size-10 items-center justify-center overflow-hidden rounded-xl bg-secondary transition-colors hover:bg-gray-200"
              disabled={disabled}
            >
              <Plus className="size-5 text-gray-400" />
            </button>
            <input
              type="text"
              value={inputValue}
              autoFocus
              disabled={disabled}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
              onChange={(e) => {
                setInputValue(e.target.value);
              }}
              placeholder="Send Message"
              className="flex-1 bg-transparent outline-none placeholder:text-text-secondary disabled:opacity-50"
            />
          </div>
          <button
            onClick={handleSubmit}
            disabled={disabled || !inputValue.trim()}
            className="flex size-10 items-center justify-center overflow-hidden rounded-xl bg-secondary transition-colors hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <AnimatePresence>
              {arrow && (
                <motion.span
                  initial={{ rotate: -90, x: "150%" }}
                  animate={{
                    rotate: inputValue ? 0 : -90,
                    x: 0,
                  }}
                  exit={{
                    y: "-150%",
                  }}
                >
                  <ArrowUp className="stroke-[2.5] size-5" />
                </motion.span>
              )}
            </AnimatePresence>
          </button>
        </div>
      </div>
    </div>
  );
}
