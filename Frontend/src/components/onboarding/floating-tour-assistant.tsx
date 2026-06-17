"use client";

import { m } from "framer-motion";
import { Bot } from "lucide-react";

import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { cn } from "@/lib/utils";

type FloatingTourAssistantProps = {
  line: string;
  experienceLabel?: string;
  className?: string;
};

/** Mini AI persona above the step card during interactive demos. */
export function FloatingTourAssistant({
  line,
  experienceLabel,
  className,
}: FloatingTourAssistantProps) {
  const reduced = useReducedMotion();

  return (
    <m.div
      initial={reduced ? false : { opacity: 0, y: 8, scale: 0.96 }}
      animate={reduced ? undefined : { opacity: 1, y: 0, scale: 1 }}
      className={cn(
        "mb-2 flex max-w-[min(22rem,calc(100vw-1.5rem))] items-start gap-2.5 rounded-2xl border border-border/70",
        "bg-surface/95 px-3 py-2.5 shadow-md backdrop-blur-md",
        className,
      )}
    >
      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-600/12 dark:bg-brand-100/10">
        <Bot className="h-4 w-4 text-brand-600 dark:text-brand-100" aria-hidden />
      </span>
      <div className="min-w-0">
        {experienceLabel && (
          <p className="text-[10px] font-semibold uppercase tracking-wider text-brand-700 dark:text-brand-100">
            {experienceLabel}
          </p>
        )}
        <p className="text-sm leading-snug text-fg">{line}</p>
      </div>
    </m.div>
  );
}
