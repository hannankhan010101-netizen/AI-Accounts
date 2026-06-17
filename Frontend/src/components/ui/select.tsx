"use client";
import * as React from "react";
import { cn } from "@/lib/utils";

export const Select = React.forwardRef<
  HTMLSelectElement,
  React.SelectHTMLAttributes<HTMLSelectElement>
>(({ className, ...rest }, ref) => (
  <select
    ref={ref}
    className={cn(
      "h-10 w-full rounded-md border border-border bg-surface-elevated px-3 text-sm text-fg motion-safe-transition hover:border-border-strong focus:border-brand focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-ring)] max-md:h-11 max-md:text-base",
      className,
    )}
    {...rest}
  />
));
Select.displayName = "Select";
