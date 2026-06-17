"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";

import { LAZY_TOUR_LOADERS } from "@/lib/tour/lazy-registry";
import { preloadCommonTours, preloadTour, preloadToursForPath } from "@/lib/tour/registry";

/** Route-aware + idle preload for tour code chunks. */
export function useTourPreload() {
  const pathname = usePathname();

  useEffect(() => {
    preloadToursForPath(pathname);
  }, [pathname]);

  useEffect(() => {
    if (typeof window === "undefined" || !("requestIdleCallback" in window)) {
      preloadCommonTours();
      return;
    }
    const id = window.requestIdleCallback(
      () => {
        preloadCommonTours();
        for (const tourId of Object.keys(LAZY_TOUR_LOADERS)) {
          void preloadTour(tourId);
        }
      },
      { timeout: 4000 },
    );
    return () => window.cancelIdleCallback(id);
  }, []);
}
