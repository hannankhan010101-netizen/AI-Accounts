/** Enterprise motion design tokens — transform-only, GPU-friendly. */

export const motionDuration = {
  instant: 0.08,
  fast: 0.15,
  normal: 0.22,
  slow: 0.32,
} as const;

export const motionDurationMs = {
  instant: 80,
  fast: 150,
  normal: 220,
  slow: 320,
} as const;

export const motionSpring = {
  snappy: { type: "spring" as const, stiffness: 420, damping: 32, mass: 0.8 },
  soft: { type: "spring" as const, stiffness: 280, damping: 28, mass: 1 },
  gentle: { type: "spring" as const, stiffness: 200, damping: 26, mass: 1.1 },
} as const;

export const motionZIndex = {
  tour: 70,
  tourTooltip: 72,
  tourFab: 71,
  assistant: 73,
} as const;
