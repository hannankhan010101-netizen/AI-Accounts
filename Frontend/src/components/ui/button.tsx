"use client";
import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { brandSolidClasses } from "@/lib/design-tokens/brand-surfaces";
import { cn } from "@/lib/utils";

const buttonStyles = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium motion-safe-transition motion-safe-active focus:outline-none focus-visible:ring-2 focus-visible:ring-brand/50 focus-visible:ring-offset-2 focus-visible:ring-offset-surface disabled:opacity-50 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        primary: brandSolidClasses,
        secondary:
          "bg-surface-elevated text-fg border border-border-subtle hover:bg-canvas hover:border-border",
        ghost: "text-fg-muted hover:bg-canvas hover:text-fg",
        danger: "bg-status-danger text-white shadow-sm hover:opacity-90",
        outline:
          "border border-border bg-surface text-fg hover:bg-canvas hover:border-border-strong",
      },
      size: {
        sm: "h-8 px-3 max-md:min-h-10",
        md: "h-10 px-4",
        lg: "h-11 px-6",
        icon: "h-11 w-11 shrink-0 p-0",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonStyles> {
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...rest }, ref) => {
    const Comp = asChild ? Slot : "button";
    return <Comp ref={ref} className={cn(buttonStyles({ variant, size }), className)} {...rest} />;
  },
);
Button.displayName = "Button";
