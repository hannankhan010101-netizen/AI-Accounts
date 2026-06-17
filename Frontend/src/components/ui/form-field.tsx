"use client";
import { cloneElement, isValidElement, useId } from "react";

import { Label } from "./label";
import { cn } from "@/lib/utils";

interface FormFieldProps {
  label: string;
  htmlFor?: string;
  error?: string;
  required?: boolean;
  className?: string;
  children: React.ReactNode;
}

export function FormField({ label, htmlFor, error, required, className, children }: FormFieldProps) {
  const autoId = useId();
  const fieldId = htmlFor ?? autoId;
  const errorId = error ? `${fieldId}-error` : undefined;

  const control =
    isValidElement(children) && !htmlFor
      ? cloneElement(children as React.ReactElement<Record<string, unknown>>, {
          id: (children as React.ReactElement<{ id?: string }>).props.id ?? fieldId,
          "aria-invalid": error ? true : undefined,
          "aria-describedby": errorId,
        })
      : isValidElement(children) && htmlFor
        ? cloneElement(children as React.ReactElement<Record<string, unknown>>, {
            id: (children as React.ReactElement<{ id?: string }>).props.id ?? fieldId,
            "aria-invalid": error ? true : undefined,
            "aria-describedby": errorId,
          })
        : children;

  return (
    <div className={cn("space-y-1", className)}>
      <Label htmlFor={fieldId}>
        {label}
        {required && <span className="ml-0.5 text-status-danger">*</span>}
      </Label>
      {control}
      {error && (
        <p id={errorId} role="alert" className="text-xs text-status-danger">
          {error}
        </p>
      )}
    </div>
  );
}
