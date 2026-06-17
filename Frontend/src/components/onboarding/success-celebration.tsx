"use client";

import { m } from "framer-motion";
import { CheckCircle2, X } from "lucide-react";

import { Card } from "@/components/ui/card";
import { celebrationVariants } from "@/lib/motion/onboarding-variants";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";

type SuccessCelebrationProps = {
  title: string;
  message: string;
  onDismiss: () => void;
};

export function SuccessCelebration({ title, message, onDismiss }: SuccessCelebrationProps) {
  const reduced = useReducedMotion();

  return (
    <m.div
      role="status"
      initial={reduced ? false : "hidden"}
      animate={reduced ? undefined : "visible"}
      exit={reduced ? undefined : "exit"}
      variants={celebrationVariants}
      className="fixed bottom-24 left-4 right-4 z-tour mx-auto max-w-md md:left-auto md:right-6"
    >
      <Card
        variant="glass"
        className="brand-glow flex items-start gap-3 overflow-hidden p-4 shadow-premium"
      >
      <m.div
        initial={reduced ? false : { scale: 0 }}
        animate={reduced ? undefined : { scale: 1 }}
        transition={{ type: "spring", stiffness: 420, damping: 22, delay: 0.05 }}
        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-status-success/15"
      >
        <CheckCircle2 className="h-5 w-5 text-status-success" aria-hidden />
      </m.div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-semibold text-fg">{title}</p>
        <p className="text-sm text-fg-muted">{message}</p>
      </div>
      <button
        type="button"
        onClick={onDismiss}
        className="shrink-0 rounded-lg p-1.5 text-fg-muted hover:bg-canvas focus-ring"
        aria-label="Dismiss"
      >
        <X className="h-4 w-4" aria-hidden />
      </button>
      </Card>
    </m.div>
  );
}
