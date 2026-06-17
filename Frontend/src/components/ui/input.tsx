"use client";
import * as React from "react";
import { cn } from "@/lib/utils";

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...rest }, ref) => (
    <input
      ref={ref}
      className={cn(
        "h-10 w-full rounded-md border border-border bg-surface-elevated px-3 text-sm text-fg placeholder:text-fg-muted motion-safe-transition hover:border-border-strong focus:border-brand focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-ring)] max-md:h-11 max-md:text-base",
        className,
      )}
      {...rest}
    />
  ),
);
Input.displayName = "Input";
