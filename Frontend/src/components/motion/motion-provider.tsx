"use client";

import { LazyMotion, MotionConfig, domAnimation } from "framer-motion";
import type { ReactNode } from "react";

import { useReducedMotion } from "@/lib/motion/use-reduced-motion";

/**
 * Global motion config — respects reduced motion, uses transform-only defaults.
 */
export function MotionProvider({ children }: { children: ReactNode }) {
  const reduced = useReducedMotion();

  return (
    <LazyMotion features={domAnimation} strict>
      <MotionConfig
        reducedMotion={reduced ? "always" : "user"}
        transition={{ type: "tween", duration: reduced ? 0.01 : 0.22 }}
      >
        {children}
      </MotionConfig>
    </LazyMotion>
  );
}
