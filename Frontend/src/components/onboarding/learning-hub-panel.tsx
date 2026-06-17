"use client";

import type { ReactNode } from "react";
import { m } from "framer-motion";

import { hubPanelVariants } from "@/lib/motion/onboarding-variants";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { cn } from "@/lib/utils";

type LearningHubPanelProps = {
  title: string;
  subtitle?: string;
  personaLabel?: string;
  children: ReactNode;
  className?: string;
};

export function LearningHubPanel({
  title,
  subtitle,
  personaLabel,
  children,
  className,
}: LearningHubPanelProps) {
  const reduced = useReducedMotion();

  return (
    <m.div
      role="menu"
      initial={reduced ? false : "hidden"}
      animate={reduced ? undefined : "visible"}
      exit={reduced ? undefined : "exit"}
      variants={hubPanelVariants}
      className={cn(
        "onboarding-glass onboarding-card mb-2 w-[min(21rem,calc(100vw-2rem))] overflow-hidden rounded-2xl",
        className,
      )}
    >
      <div className="onboarding-mesh border-b border-border/60 px-4 py-3">
        <p className="text-[10px] font-semibold uppercase tracking-widest text-fg-muted">
          Learning hub
        </p>
        <h2 className="mt-0.5 text-base font-semibold text-fg">{title}</h2>
        {subtitle && <p className="mt-0.5 text-xs leading-relaxed text-fg-muted">{subtitle}</p>}
        {personaLabel && (
          <span className="mt-2 inline-block rounded-full border border-border/80 bg-surface/80 px-2 py-0.5 text-[10px] font-medium text-fg-muted">
            Personalized for {personaLabel}
          </span>
        )}
      </div>
      <div className="max-h-[min(24rem,55vh)] overflow-y-auto p-2">{children}</div>
    </m.div>
  );
}
