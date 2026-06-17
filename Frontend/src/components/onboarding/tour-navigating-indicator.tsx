"use client";

import { m, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

import { pathnameMatchesRoute } from "@/lib/tour/sidebar-navigation";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { useTour } from "@/lib/tour/tour-context";
import { useTourUIStore } from "@/stores/onboarding/tour-ui-store";

export function TourNavigatingIndicator() {
  const navigating = useTourUIStore((s) => s.workflowNavigating);
  const reduced = useReducedMotion();
  const pathname = usePathname();
  const { running, currentStep } = useTour();
  const [routeBlocked, setRouteBlocked] = useState(false);

  useEffect(() => {
    if (!running || !currentStep?.validation || currentStep.validation.type !== "routeMatch") {
      setRouteBlocked(false);
      return;
    }
    const expected = currentStep.validation.pathname;
    const timer = window.setTimeout(() => {
      setRouteBlocked(!pathnameMatchesRoute(pathname, expected));
    }, 4500);
    return () => window.clearTimeout(timer);
  }, [running?.definition.id, running?.stepIndex, currentStep?.id, currentStep?.validation, pathname]);

  useEffect(() => {
    if (
      currentStep?.validation?.type === "routeMatch" &&
      pathnameMatchesRoute(pathname, currentStep.validation.pathname)
    ) {
      setRouteBlocked(false);
    }
  }, [pathname, currentStep?.validation]);

  const visible = navigating || routeBlocked;

  return (
    <AnimatePresence>
      {visible && (
        <m.div
          role="status"
          initial={reduced ? false : { opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={reduced ? undefined : { opacity: 0, y: -8 }}
          className="pointer-events-none fixed left-0 right-0 top-0 z-[calc(var(--z-tour)+4)] flex justify-center pt-2"
        >
          <span className="inline-flex items-center gap-2 rounded-full border border-border/80 bg-surface/95 px-4 py-1.5 text-xs font-medium text-fg shadow-md">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-600/40 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-brand-600 dark:bg-brand-100" />
            </span>
            {navigating
              ? "Opening the next step for you…"
              : "Still opening the right page — use Next or wait a moment"}
          </span>
        </m.div>
      )}
    </AnimatePresence>
  );
}
