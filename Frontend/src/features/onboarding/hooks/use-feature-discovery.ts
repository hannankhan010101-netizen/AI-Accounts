"use client";

import { useMemo } from "react";
import { usePathname } from "next/navigation";

import { useTour } from "@/lib/tour/tour-context";
import { rankFeatureHints } from "@/lib/tour/hint-ranker";
import type { FeatureHint } from "@/lib/tour/types";

/**
 * Context-aware feature discovery — ranks hints for current route + persona.
 */
export function useFeatureDiscovery(limit = 5): {
  hints: FeatureHint[];
  dismiss: (hintId: string) => void;
  pathname: string;
} {
  const pathname = usePathname();
  const { featureHints, dismissFeatureHint, persona, progress } = useTour();

  const hints = useMemo(() => {
    const ranked = rankFeatureHints(featureHints, { pathname, persona, progress });
    return ranked.slice(0, limit);
  }, [featureHints, pathname, persona, progress, limit]);

  return {
    hints,
    dismiss: dismissFeatureHint,
    pathname,
  };
}
