"use client";

import * as React from "react";
import type { LucideIcon } from "lucide-react";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

interface AuthInputFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  icon: LucideIcon;
  error?: string;
  trailing?: React.ReactNode;
}

export const AuthInputField = React.forwardRef<HTMLInputElement, AuthInputFieldProps>(
  ({ label, icon: Icon, error, trailing, className, id, required, ...rest }, ref) => {
    const autoId = React.useId();
    const fieldId = id ?? autoId;
    const errorId = error ? `${fieldId}-error` : undefined;

    return (
      <div className="space-y-1.5">
        <Label htmlFor={fieldId} className="text-[var(--text-label)] font-medium text-fg">
          {label}
          {required && <span className="ml-0.5 text-status-danger">*</span>}
        </Label>
        <div className="relative">
          <span
            aria-hidden
            className="pointer-events-none absolute inset-y-0 left-0 flex w-10 items-center justify-center text-fg-muted"
          >
            <Icon className="h-4 w-4" strokeWidth={1.75} />
          </span>
          <Input
            ref={ref}
            id={fieldId}
            aria-invalid={error ? true : undefined}
            aria-describedby={errorId}
            className={cn(
              "h-11 border-border-subtle bg-surface pl-10 pr-10 text-[var(--text-body)] shadow-xs placeholder:text-fg-muted/70",
              "focus:border-brand focus:shadow-[0_0_0_3px_var(--focus-ring)]",
              trailing && "pr-11",
              className,
            )}
            required={required}
            {...rest}
          />
          {trailing && (
            <div className="absolute inset-y-0 right-0 flex items-center pr-1">{trailing}</div>
          )}
        </div>
        {error && (
          <p id={errorId} role="alert" className="text-xs text-status-danger">
            {error}
          </p>
        )}
      </div>
    );
  },
);
AuthInputField.displayName = "AuthInputField";
