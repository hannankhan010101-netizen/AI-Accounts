"use client";

import { Button } from "@/components/ui/button";

interface DocumentDraftBannerProps {
  savedAt: string | null;
  onRestore: () => void;
  onDiscard: () => void;
}

export function DocumentDraftBanner({ savedAt, onRestore, onDiscard }: DocumentDraftBannerProps) {
  const when = savedAt ? new Date(savedAt).toLocaleString() : "earlier";
  return (
    <div
      className="mb-4 flex flex-wrap items-center justify-between gap-2 rounded-md border border-status-warning/30 bg-status-warning/10 px-3 py-2 text-sm text-fg"
      role="status"
    >
      <span>Unsaved draft from {when}</span>
      <div className="flex gap-2">
        <Button type="button" variant="outline" size="sm" onClick={onRestore}>
          Restore draft
        </Button>
        <Button type="button" variant="ghost" size="sm" onClick={onDiscard}>
          Discard
        </Button>
      </div>
    </div>
  );
}
