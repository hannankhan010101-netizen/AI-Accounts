"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export const Checkbox = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(({ className, id, ...rest }, ref) => {
  const input = (
    <input
      ref={ref}
      id={id}
      type="checkbox"
      className={cn(
        "h-4 w-4 shrink-0 rounded border-border-strong text-brand focus:ring-brand/40 motion-safe-transition",
        className,
      )}
      {...rest}
    />
  );
  const hitAreaClass = cn(
    "inline-flex min-h-11 min-w-11 cursor-pointer items-center justify-center",
    className?.includes("pointer-events-none") && "pointer-events-none",
  );
  if (id) {
    return (
      <label htmlFor={id} className={hitAreaClass}>
        {input}
      </label>
    );
  }
  return <span className={hitAreaClass}>{input}</span>;
});
Checkbox.displayName = "Checkbox";
