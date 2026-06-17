/** Tailwind-aligned breakpoints (min-width). */
export const BREAKPOINTS = {
  xs: 375,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  "2xl": 1536,
} as const;

export type BreakpointKey = keyof typeof BREAKPOINTS;

/** Matches Tailwind `max-md:` — viewport width strictly below md. */
export const MOBILE_MEDIA_QUERY = `(max-width: ${BREAKPOINTS.md - 1}px)`;

export function mediaQueryFor(breakpoint: BreakpointKey): string {
  return `(min-width: ${BREAKPOINTS[breakpoint]}px)`;
}

export function mediaQueryBelow(breakpoint: BreakpointKey): string {
  return `(max-width: ${BREAKPOINTS[breakpoint] - 1}px)`;
}
