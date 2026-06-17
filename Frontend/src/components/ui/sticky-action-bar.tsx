"use client";

import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export interface StickyActionBarProps {
  children: ReactNode;
  className?: string;
  /** Desktop sticky below top bar; mobile fixed bottom */
  position?: "auto" | "bottom" | "top";
}

export function StickyActionBar({ children, className, position = "auto" }: StickyActionBarProps) {
  return (
    <div
      className={cn(
        "gpu-layer z-30 flex flex-wrap items-center justify-end gap-2 border-border-subtle bg-surface/95 p-3 backdrop-blur-md motion-safe-transition",
        position === "bottom" && "fixed inset-x-0 bottom-0 border-t pb-safe",
        position === "top" && "sticky top-0 border-b",
        position === "auto" &&
          "max-lg:fixed max-lg:inset-x-0 max-lg:bottom-0 max-lg:border-t max-lg:pb-safe lg:sticky lg:top-0 lg:border-b lg:shadow-sm",
        className,
      )}
    >
      {children}
    </div>
  );
}
