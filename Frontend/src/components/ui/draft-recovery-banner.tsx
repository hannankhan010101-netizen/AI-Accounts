"use client";

import { Button } from "@/components/ui/button";
import { InlineAlert } from "@/components/ui/inline-alert";

interface DraftRecoveryBannerProps {
  visible: boolean;
  onRestore: () => void;
  onDiscard: () => void;
}

export function DraftRecoveryBanner({ visible, onRestore, onDiscard }: DraftRecoveryBannerProps) {
  if (!visible) return null;

  return (
    <InlineAlert variant="info" className="mb-4">
      <span>Unsaved draft from a previous session. Restore it or discard?</span>
      <div className="flex gap-2">
        <Button type="button" size="sm" variant="outline" onClick={onDiscard}>
          Discard
        </Button>
        <Button type="button" size="sm" onClick={onRestore}>
          Restore draft
        </Button>
      </div>
    </InlineAlert>
  );
}
