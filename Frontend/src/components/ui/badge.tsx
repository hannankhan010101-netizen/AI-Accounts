"use client";

import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeStyles = cva(
  "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium motion-safe-transition",
  {
    variants: {
      variant: {
        default: "bg-canvas text-fg-muted",
        brand: "bg-brand-50 text-brand-700 dark:bg-brand-100/15 dark:text-brand-300",
        success: "bg-status-success/10 text-status-success",
        warning: "bg-status-warning/10 text-status-warning",
        danger: "bg-status-danger/10 text-status-danger",
        outline: "border border-border bg-surface text-fg-muted",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeStyles> {}

export function Badge({ className, variant, ...rest }: BadgeProps) {
  return <span className={cn(badgeStyles({ variant }), className)} {...rest} />;
}
