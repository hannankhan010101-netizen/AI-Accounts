"use client";

import { m } from "framer-motion";
import { memo, useId, useMemo } from "react";

import type { TargetRect } from "@/lib/tour/target-resolver";
import { toSpotlightRect } from "@/lib/tour/target-resolver";
import { motionSpring } from "@/lib/motion/tokens";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { cn } from "@/lib/utils";

const RADIUS = 12;

type SpotlightOverlayProps = {
  rect: TargetRect;
  secondaryRect?: TargetRect | null;
};

function SpotlightRing({
  hole,
  reduced,
}: {
  hole: TargetRect;
  reduced: boolean;
}) {
  return (
    <m.div
      className={cn(
        "pointer-events-none fixed z-[calc(var(--z-tour)+1)]",
        "rounded-[14px] ring-2 ring-brand/70 ring-offset-2 ring-offset-transparent",
        "dark:ring-brand-400/55",
        "shadow-brand-glow",
      )}
      aria-hidden
      initial={false}
      animate={{
        top: hole.top,
        left: hole.left,
        width: hole.width,
        height: hole.height,
      }}
      transition={reduced ? { duration: 0.01 } : motionSpring.soft}
    />
  );
}

/** Scrim + blur only OUTSIDE spotlight hole(s) — hole stays sharp. */
export const SpotlightOverlay = memo(function SpotlightOverlay({
  rect,
  secondaryRect,
}: SpotlightOverlayProps) {
  const reduced = useReducedMotion();
  const maskId = useId().replace(/:/g, "");
  const hole = useMemo(() => toSpotlightRect(rect), [rect]);
  const hole2 = useMemo(
    () => (secondaryRect ? toSpotlightRect(secondaryRect) : null),
    [secondaryRect],
  );
  const holes = hole2 ? [hole, hole2] : [hole];

  return (
    <>
      <svg
        className="pointer-events-none fixed inset-0 z-tour h-full w-full"
        aria-hidden
      >
        <defs>
          <mask
            id={maskId}
            maskUnits="userSpaceOnUse"
            x="0"
            y="0"
            width="100%"
            height="100%"
          >
            <rect width="100%" height="100%" fill="white" />
            {holes.map((h, i) => (
              <rect
                key={i}
                x={h.left}
                y={h.top}
                width={h.width}
                height={h.height}
                rx={RADIUS}
                fill="black"
              />
            ))}
          </mask>
        </defs>
      </svg>
      <m.div
        className="pointer-events-none fixed inset-0 z-tour bg-[var(--onboarding-scrim)] backdrop-blur-[2px]"
        style={{
          mask: `url(#${maskId})`,
          WebkitMask: `url(#${maskId})`,
        }}
        aria-hidden
        initial={{ opacity: 0 }}
        animate={{ opacity: reduced ? 0.92 : 0.92 }}
        exit={{ opacity: 0 }}
        transition={{ duration: reduced ? 0.01 : 0.28 }}
      />
      {holes.map((h, i) => (
        <SpotlightRing key={i} hole={h} reduced={reduced} />
      ))}
    </>
  );
});
