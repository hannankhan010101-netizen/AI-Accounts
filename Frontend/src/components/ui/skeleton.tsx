"use client";

import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const skeletonStyles = cva("rounded-md", {
  variants: {
    variant: {
      text: "h-4 w-full max-w-[12rem]",
      block: "h-10 w-full",
      circle: "h-10 w-10 rounded-full",
      metric: "h-8 w-24",
      chart: "h-32 w-full rounded-lg",
    },
    shimmer: {
      true: "skeleton-shimmer",
      false: "animate-pulse bg-surface-muted",
    },
  },
  defaultVariants: { variant: "block", shimmer: true },
});

export interface SkeletonProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof skeletonStyles> {}

export function Skeleton({ className, variant, shimmer, ...rest }: SkeletonProps) {
  return <div className={cn(skeletonStyles({ variant, shimmer }), className)} aria-hidden {...rest} />;
}

export function SkeletonGroup({ className, children }: { className?: string; children: React.ReactNode }) {
  return <div className={cn("space-y-2", className)}>{children}</div>;
}
