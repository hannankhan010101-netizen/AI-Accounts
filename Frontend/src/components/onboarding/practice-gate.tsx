"use client";

import { useEffect } from "react";

import type { TargetRect } from "@/lib/tour/target-resolver";
import { toSpotlightRect } from "@/lib/tour/target-resolver";

type PracticeGateProps = {
  rect: TargetRect | null;
  tourTargetId: string | null;
  onTargetClicked: () => void;
};

/**
 * Blocks clicks outside the spotlight hole; advances when the user clicks the target.
 */
export function PracticeGate({ rect, tourTargetId, onTargetClicked }: PracticeGateProps) {
  useEffect(() => {
    if (!tourTargetId) return;
    function onClick(e: MouseEvent) {
      const target = e.target as HTMLElement | null;
      if (!target) return;
      const el = document.querySelector(`[data-tour="${tourTargetId}"]`);
      if (el?.contains(target)) {
        onTargetClicked();
      }
    }
    document.addEventListener("click", onClick, true);
    return () => document.removeEventListener("click", onClick, true);
  }, [tourTargetId, onTargetClicked]);

  if (!rect) return null;
  const hole = toSpotlightRect(rect);

  return (
    <div
      className="fixed inset-0 z-[calc(var(--z-tour))] pointer-events-auto"
      aria-hidden
      style={{
        clipPath: `polygon(
          0% 0%, 0% 100%, 100% 100%, 100% 0%, 0% 0%,
          ${hole.left}px 0%,
          ${hole.left}px ${hole.top}px,
          ${hole.left + hole.width}px ${hole.top}px,
          ${hole.left + hole.width}px ${hole.top + hole.height}px,
          ${hole.left}px ${hole.top + hole.height}px,
          ${hole.left}px 0%
        )`,
      }}
    />
  );
}
