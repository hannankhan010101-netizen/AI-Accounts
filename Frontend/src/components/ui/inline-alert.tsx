"use client";

import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const alertStyles = cva(
  "flex flex-wrap items-center justify-between gap-3 rounded-md border px-4 py-3 text-sm motion-safe-transition",
  {
    variants: {
      variant: {
        info: "border-status-info/30 bg-status-info/10 text-fg",
        success: "border-status-success/30 bg-status-success/10 text-fg",
        warning: "border-status-warning/30 bg-status-warning/10 text-fg",
        error: "border-status-danger/30 bg-status-danger/10 text-fg",
      },
    },
    defaultVariants: { variant: "info" },
  },
);

export interface InlineAlertProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof alertStyles> {
  role?: "alert" | "status";
}

export function InlineAlert({
  className,
  variant,
  role = "status",
  children,
  ...rest
}: InlineAlertProps) {
  return (
    <div className={cn(alertStyles({ variant }), className)} role={role} {...rest}>
      {children}
    </div>
  );
}
