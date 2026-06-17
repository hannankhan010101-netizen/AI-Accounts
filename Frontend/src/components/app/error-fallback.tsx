"use client";

import { Button } from "@/components/ui/button";

interface ErrorFallbackProps {
  title?: string;
  message?: string;
  reset?: () => void;
}

export function ErrorFallback({
  title = "Something went wrong",
  message = "This page could not be loaded. Your data was not changed.",
  reset,
}: ErrorFallbackProps) {
  return (
    <div
      className="mx-auto max-w-md rounded-lg border border-border bg-surface p-6 text-center shadow-sm"
      role="alert"
    >
      <h2 className="text-lg font-semibold text-fg">{title}</h2>
      <p className="mt-2 text-sm text-fg-muted">{message}</p>
      <div className="mt-6 flex flex-wrap justify-center gap-2">
        {reset ? (
          <Button type="button" onClick={reset}>
            Try again
          </Button>
        ) : null}
        <Button type="button" variant="outline" onClick={() => window.history.back()}>
          Go back
        </Button>
        <Button type="button" variant="ghost" onClick={() => window.location.assign("/dashboard")}>
          Dashboard
        </Button>
      </div>
    </div>
  );
}
