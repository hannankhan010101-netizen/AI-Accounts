"use client";

import { m } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Compass, X } from "lucide-react";
import { memo } from "react";

import { Button } from "@/components/ui/button";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { staggerItem } from "@/lib/motion/variants";
import { trackFeatureAdoption } from "@/lib/tour/analytics";
import type { FeatureHint } from "@/lib/tour/types";
import { cn } from "@/lib/utils";

type FeatureHintCardProps = {
  hint: FeatureHint;
  pathname: string;
  companyId: string | null;
  onDismiss: (id: string) => void;
  onStartTour: (tourId: string, href?: string) => void;
  className?: string;
};

export const FeatureHintCard = memo(function FeatureHintCard({
  hint,
  pathname,
  companyId,
  onDismiss,
  onStartTour,
  className,
}: FeatureHintCardProps) {
  const router = useRouter();
  const reduced = useReducedMotion();

  function handleCta() {
    trackFeatureAdoption(hint.id, {
      pathname,
      companyId,
      tourId: hint.tourId,
    });
    if (hint.href) router.push(hint.href);
    if (hint.tourId) onStartTour(hint.tourId, hint.href);
  }

  return (
    <m.li
      variants={reduced ? undefined : staggerItem}
      className={cn(
        "flex flex-col gap-3 rounded-lg border border-border bg-canvas/40 p-4 sm:flex-row sm:items-center sm:justify-between",
        className,
      )}
    >
      <div className="min-w-0">
        <p className="font-medium text-fg">{hint.title}</p>
        <p className="mt-0.5 text-sm text-fg-muted">{hint.body}</p>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        {hint.tourId ? (
          <Button type="button" variant="primary" size="sm" onClick={handleCta}>
            <Compass className="mr-1.5 h-3.5 w-3.5" aria-hidden />
            {hint.ctaLabel}
          </Button>
        ) : hint.href ? (
          <Link href={hint.href} onClick={() => trackFeatureAdoption(hint.id, { pathname, companyId })}>
            <Button type="button" variant="primary" size="sm">
              {hint.ctaLabel}
            </Button>
          </Link>
        ) : null}
        <button
          type="button"
          onClick={() => onDismiss(hint.id)}
          className="rounded-md p-1.5 text-fg-muted hover:bg-surface focus-ring"
          aria-label={`Dismiss: ${hint.title}`}
        >
          <X className="h-4 w-4" aria-hidden />
        </button>
      </div>
    </m.li>
  );
});
