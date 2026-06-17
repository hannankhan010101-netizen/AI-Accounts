"use client";

import { WifiOff } from "lucide-react";

import { InlineAlert } from "@/components/ui/inline-alert";
import { useOnlineStatus } from "@/lib/network/use-online-status";

export function OfflineBanner() {
  const online = useOnlineStatus();

  if (online) return null;

  return (
    <InlineAlert
      variant="warning"
      role="status"
      aria-live="polite"
      className="rounded-none border-x-0"
    >
      <span className="flex items-center justify-center gap-2">
        <WifiOff className="h-4 w-4 shrink-0" aria-hidden />
        <span>
          You&apos;re offline. Changes are saved locally where supported; they will sync when
          you&apos;re back online.
        </span>
      </span>
    </InlineAlert>
  );
}
