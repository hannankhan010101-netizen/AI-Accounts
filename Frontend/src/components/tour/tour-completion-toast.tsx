"use client";

import { useEffect } from "react";

import { SuccessCelebration } from "@/components/onboarding/success-celebration";
import { useTour } from "@/lib/tour/tour-context";

export function TourCompletionToast() {
  const { completionToast, completionMessage, clearCompletionToast } = useTour();

  useEffect(() => {
    if (!completionToast) return;
    const t = window.setTimeout(() => clearCompletionToast(), 7000);
    return () => window.clearTimeout(t);
  }, [completionToast, clearCompletionToast]);

  if (!completionToast) return null;

  return (
    <SuccessCelebration
      title="Nice work"
      message={
        completionMessage ??
        `You completed “${completionToast}”. Your progress is saved.`
      }
      onDismiss={clearCompletionToast}
    />
  );
}
