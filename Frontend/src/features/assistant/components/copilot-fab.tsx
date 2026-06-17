"use client";

import { m } from "framer-motion";
import { Sparkles } from "lucide-react";

import { t } from "@/features/assistant/i18n";
import { useAssistant } from "@/features/assistant/providers/assistant-provider";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { useCopilotStore } from "@/stores/assistant/copilot-store";
import { brandSolidClasses } from "@/lib/design-tokens/brand-surfaces";
import { cn } from "@/lib/utils";

export function CopilotFAB() {
  const reduced = useReducedMotion();
  const { openCopilot } = useAssistant();
  const open = useCopilotStore((s) => s.open);
  const setOpen = useCopilotStore((s) => s.setOpen);

  if (open) return null;

  return (
    <m.button
      type="button"
      initial={reduced ? false : { scale: 0.9, opacity: 0 }}
      animate={reduced ? undefined : { scale: 1, opacity: 1 }}
      whileHover={reduced ? undefined : { scale: 1.04 }}
      whileTap={reduced ? undefined : { scale: 0.96 }}
      transition={{ type: "spring", stiffness: 400, damping: 28 }}
      onClick={() => {
        setOpen(true);
        openCopilot({ mode: "erp" });
      }}
      className={cn(
        "no-print fixed right-4 z-[calc(var(--z-tour)+2)]",
        "bottom-[calc(var(--bottom-nav-height)+env(safe-area-inset-bottom,0px)+1.5rem)] md:bottom-6 md:right-6",
        "flex h-14 w-14 items-center justify-center rounded-full",
        brandSolidClasses,
        "brand-glow rounded-full",
      )}
      aria-label={t("en", "openCopilot")}
    >
      <Sparkles className="h-6 w-6" aria-hidden />
    </m.button>
  );
}
