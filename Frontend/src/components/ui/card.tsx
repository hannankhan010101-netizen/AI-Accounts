"use client";

import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const cardStyles = cva("rounded-xl motion-safe-transition", {
  variants: {
    variant: {
      default:
        "border border-border bg-surface dark:border-transparent dark:bg-surface-elevated/90 dark:shadow-md",
      elevated: "surface-elevated rounded-xl",
      glass:
        "surface-glass border border-border-subtle rounded-xl dark:border-transparent dark:shadow-sm",
      accent:
        "border border-border bg-surface shadow-sm before:block before:h-0.5 before:w-full before:rounded-t-xl before:bg-gradient-to-r before:from-brand-600/60 before:to-accent-sage/40 dark:border-transparent dark:bg-surface-elevated/90 dark:shadow-md dark:before:from-brand-500/50 dark:before:to-accent-sage/30",
      metric:
        "border border-border-subtle bg-surface-elevated p-4 shadow-sm hover:shadow-md dark:border-transparent dark:bg-surface-elevated/80 dark:shadow-md dark:hover:shadow-lg",
    },
    interactive: {
      true: "hover:-translate-y-0.5 hover:shadow-md cursor-default dark:hover:shadow-lg",
      false: "",
    },
  },
  defaultVariants: { variant: "default", interactive: false },
});

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardStyles> {}

export function Card({ className, variant, interactive, ...rest }: CardProps) {
  return <div className={cn(cardStyles({ variant, interactive }), className)} {...rest} />;
}

export function CardHeader({ className, ...rest }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex flex-col gap-1 p-4 pb-2", className)} {...rest} />;
}

export function CardTitle({ className, ...rest }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn("text-label font-semibold text-fg", className)} {...rest} />;
}

export function CardDescription({ className, ...rest }: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn("text-sm text-fg-muted", className)} {...rest} />;
}

export function CardContent({ className, ...rest }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-4 pt-0", className)} {...rest} />;
}

export function CardFooter({ className, ...rest }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "flex items-center gap-2 border-t border-border-subtle p-4 pt-3 dark:border-border-subtle/60",
        className,
      )}
      {...rest}
    />
  );
}
