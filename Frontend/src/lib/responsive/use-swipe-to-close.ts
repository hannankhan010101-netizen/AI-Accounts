"use client";

import { useCallback } from "react";

const DEFAULT_THRESHOLD = 72;

/** Close when user drags horizontally past threshold (e.g. drawer swipe-left). */
export function useSwipeToClose(
  onClose: () => void,
  direction: "left" | "right" = "left",
  threshold = DEFAULT_THRESHOLD,
) {
  return useCallback(
    (_event: MouseEvent | TouchEvent | PointerEvent, info: { offset: { x: number } }) => {
      if (direction === "left" && info.offset.x < -threshold) onClose();
      if (direction === "right" && info.offset.x > threshold) onClose();
    },
    [onClose, direction, threshold],
  );
}
