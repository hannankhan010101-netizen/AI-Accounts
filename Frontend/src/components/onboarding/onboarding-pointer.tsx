"use client";

import type { Placement } from "@floating-ui/react";

import { cn } from "@/lib/utils";

/** Small arrow linking the step card to the highlighted control. */
export function OnboardingPointer({
  placement,
  className,
}: {
  placement: Placement;
  className?: string;
}) {
  const side = placement.split("-")[0];

  return (
    <span
      className={cn(
        "pointer-events-none absolute block h-2.5 w-2.5 rotate-45 border border-border/80 bg-surface",
        side === "top" && "bottom-[-5px] left-6 border-t-0 border-l-0",
        side === "bottom" && "top-[-5px] left-6 border-b-0 border-r-0",
        side === "left" && "right-[-5px] top-5 border-b-0 border-l-0",
        side === "right" && "left-[-5px] top-5 border-t-0 border-r-0",
        className,
      )}
      aria-hidden
    />
  );
}
