"use client";

import { useEffect } from "react";

import { ErrorFallback } from "@/components/app/error-fallback";

export default function AppError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("[app-error]", error);
  }, [error]);

  return (
    <div className="flex min-h-[40vh] items-center justify-center p-6">
      <ErrorFallback
        message={error.message || "An unexpected error occurred."}
        reset={reset}
      />
    </div>
  );
}
