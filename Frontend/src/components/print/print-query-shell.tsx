"use client";

import { ApiError } from "@/lib/api/client";

interface PrintQueryShellProps {
  isLoading: boolean;
  error: unknown;
  ready: boolean;
  notFoundMessage?: string;
  children: React.ReactNode;
}

function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return "Could not load document for printing.";
}

/** Standard loading / error / not-found states for `/print/*` routes. */
export function PrintQueryShell({
  isLoading,
  error,
  ready,
  notFoundMessage = "Document not found.",
  children,
}: PrintQueryShellProps) {
  if (isLoading) {
    return <div className="p-8 text-sm text-fg-muted">Loading…</div>;
  }
  if (error) {
    return (
      <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-6 text-sm text-status-danger">
        {errorMessage(error)}
      </div>
    );
  }
  if (!ready) {
    return <div className="p-8 text-sm text-fg">{notFoundMessage}</div>;
  }
  return <>{children}</>;
}
