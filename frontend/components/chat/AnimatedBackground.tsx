"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface AnimatedBackgroundProps {
  isSubmitting?: boolean;
}

const Grad = ({ className }: { className?: string }) => (
  <div
    className={cn("flex h-full flex-col items-stretch -space-y-3", className)}
  >
    <div className="w-full flex-1 bg-accent-blue/20 blur-xl" />
    <div className="w-full flex-1 bg-accent-sky/20 blur-xl" />
    <div className="w-full flex-1 bg-accent-blue/30 blur-xl" />
    <div className="w-full flex-1 bg-card-gradient-top/20 blur-xl" />
    <div className="w-full flex-1 bg-accent-sky/20 blur-xl" />
  </div>
);

export function AnimatedBackground({ isSubmitting = false }: AnimatedBackgroundProps) {
  return (
    <motion.div
      key={`submit-${isSubmitting}`}
      initial={{
        y: "100%",
        opacity: 0.2,
      }}
      transition={{
        type: "spring",
        stiffness: 100,
        damping: 20,
      }}
      animate={{
        y: "30%",
        opacity: 0,
      }}
      className="fixed left-1/2 top-0 flex h-[100vh] w-full max-w-3xl -translate-x-1/2 z-0 pointer-events-none"
    >
      <Grad className="w-full" />
      <Grad className="w-full -translate-y-20" />
      <Grad className="w-full" />
    </motion.div>
  );
}
