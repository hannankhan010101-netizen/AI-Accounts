import type { CSSProperties } from "react";
import type { Placement } from "@floating-ui/react";

import type { TargetRect } from "@/lib/tour/target-resolver";
import type { TourStep } from "@/lib/tour/types";

/** Prefer side placement for top-bar controls so the card does not cover the header. */
export function resolveTourPlacement(
  rect: TargetRect | null,
  step: TourStep,
  centered: boolean,
): Placement {
  if (centered || !rect) return "bottom";

  const preferred = step.placement ?? "auto";
  const inHeader = rect.top < 140;
  const narrow = rect.width < 200 && rect.height < 56;

  if (preferred === "auto" || preferred === "right") {
    if (inHeader) return "bottom-start";
    return preferred === "right" ? "right" : "bottom";
  }

  if (preferred === "bottom" && inHeader) {
    return "bottom-start";
  }

  return preferred as Placement;
}

export function offsetForPlacement(
  placement: Placement,
  rect: TargetRect | null,
): number | { mainAxis: number; crossAxis: number } {
  if (!rect) return 16;
  const inHeader = rect.top < 140;
  if (placement === "right") return { mainAxis: 14, crossAxis: 0 };
  if (placement.startsWith("bottom") && inHeader) return { mainAxis: 12, crossAxis: -4 };
  return 16;
}

export function isCompactAnchoredCard(rect: TargetRect | null, centered: boolean): boolean {
  if (centered || !rect) return false;
  return rect.top < 200 || (rect.width < 320 && rect.height < 72);
}

/** Pin card below header controls when floating UI would cover them. */
export function anchoredCardStyle(
  rect: TargetRect | null,
  centered: boolean,
): CSSProperties | null {
  if (centered || !rect || typeof window === "undefined") return null;
  if (rect.top >= 120) return null;

  const anchorTop = Math.max(12, rect.top);
  const top = anchorTop + rect.height + 14;
  const left = Math.min(
    Math.max(16, rect.left),
    window.innerWidth - Math.min(320, window.innerWidth - 32),
  );

  return {
    position: "fixed",
    top,
    left,
    transform: "none",
  };
}
