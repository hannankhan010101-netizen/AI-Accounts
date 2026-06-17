"use client";

import { useCallback, useEffect, useState } from "react";

import { BREAKPOINTS, type BreakpointKey } from "@/lib/responsive/constants";

function getActiveBreakpoint(width: number): BreakpointKey {
  const keys = Object.keys(BREAKPOINTS) as BreakpointKey[];
  let active: BreakpointKey = "xs";
  for (const key of keys) {
    if (width >= BREAKPOINTS[key]) active = key;
  }
  return active;
}

export function useBreakpoint(): BreakpointKey {
  const [breakpoint, setBreakpoint] = useState<BreakpointKey>("md");

  useEffect(() => {
    const update = () => setBreakpoint(getActiveBreakpoint(window.innerWidth));
    update();
    window.addEventListener("resize", update, { passive: true });
    return () => window.removeEventListener("resize", update);
  }, []);

  return breakpoint;
}

export function useIsMobile(): boolean {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia(`(max-width: ${BREAKPOINTS.md - 1}px)`);
    const update = () => setIsMobile(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);

  return isMobile;
}

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia(query);
    const update = () => setMatches(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, [query]);

  return matches;
}

export function useIsBelow(breakpoint: BreakpointKey): boolean {
  return useMediaQuery(`(max-width: ${BREAKPOINTS[breakpoint] - 1}px)`);
}

export function useVisualViewportInset(): number {
  const [bottomInset, setBottomInset] = useState(0);

  const update = useCallback(() => {
    const vv = window.visualViewport;
    if (!vv) {
      setBottomInset(0);
      return;
    }
    const inset = Math.max(0, window.innerHeight - vv.height - vv.offsetTop);
    setBottomInset(inset);
  }, []);

  useEffect(() => {
    update();
    const vv = window.visualViewport;
    if (!vv) return;
    vv.addEventListener("resize", update);
    vv.addEventListener("scroll", update);
    return () => {
      vv.removeEventListener("resize", update);
      vv.removeEventListener("scroll", update);
    };
  }, [update]);

  return bottomInset;
}
