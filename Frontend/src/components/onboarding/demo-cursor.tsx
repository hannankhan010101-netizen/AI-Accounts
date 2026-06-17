"use client";

import { m } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import { MousePointer2 } from "lucide-react";

import { clickRippleVariants, demoCursorVariants } from "@/lib/motion/demo-cursor-variants";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import type { TargetRect } from "@/lib/tour/target-resolver";
import type { TourCursorConfig } from "@/lib/tour/types";

type DemoCursorProps = {
  targetRect: TargetRect | null;
  config?: TourCursorConfig;
};

const CURSOR_SIZE = 28;

export function DemoCursor({ targetRect, config }: DemoCursorProps) {
  const reduced = useReducedMotion();
  const [clickPulse, setClickPulse] = useState(false);
  const delayMs = config?.delayMs ?? 400;

  const destination = useMemo(() => {
    if (!targetRect) return null;
    return {
      x: targetRect.left + targetRect.width * 0.65 - CURSOR_SIZE / 2,
      y: targetRect.top + targetRect.height * 0.55 - CURSOR_SIZE / 2,
    };
  }, [targetRect]);

  useEffect(() => {
    if (!destination || reduced) return;
    const t = window.setTimeout(() => {
      if (config?.clickPulse !== false) setClickPulse(true);
    }, delayMs + 720);
    return () => window.clearTimeout(t);
  }, [destination, delayMs, config?.clickPulse, reduced]);

  useEffect(() => {
    if (!clickPulse) return;
    const t = window.setTimeout(() => setClickPulse(false), 600);
    return () => window.clearTimeout(t);
  }, [clickPulse]);

  if (!destination || reduced) return null;

  return (
    <>
      <m.div
        className="pointer-events-none fixed z-[calc(var(--z-tour)+3)]"
        initial={{ left: destination.x - 80, top: destination.y + 60, opacity: 0 }}
        animate={{
          left: destination.x,
          top: destination.y,
          opacity: 1,
        }}
        transition={{ type: "spring", stiffness: 120, damping: 18, delay: delayMs / 1000 }}
        aria-hidden
      >
        <m.div
          variants={demoCursorVariants}
          initial="hidden"
          animate="visible"
          className="flex h-7 w-7 items-center justify-center rounded-full bg-surface shadow-lg ring-2 ring-brand-600/40"
        >
          <MousePointer2 className="h-4 w-4 text-brand-700 dark:text-brand-100" />
        </m.div>
      </m.div>
      {clickPulse && (
        <m.div
          className="pointer-events-none fixed z-[calc(var(--z-tour)+2)] h-10 w-10 rounded-full border-2 border-brand-600/50"
          style={{ left: destination.x + 4, top: destination.y + 4 }}
          variants={clickRippleVariants}
          initial="hidden"
          animate="pulse"
          aria-hidden
        />
      )}
    </>
  );
}
