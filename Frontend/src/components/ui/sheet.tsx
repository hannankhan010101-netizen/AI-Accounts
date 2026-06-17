"use client";

import { AnimatePresence, m } from "framer-motion";
import { X } from "lucide-react";
import type { ReactNode } from "react";
import { useRef } from "react";

import { motionPresets } from "@/lib/motion/presets";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { useFocusTrap } from "@/lib/responsive/use-focus-trap";
import { useLockBodyScroll } from "@/lib/responsive/use-lock-body-scroll";
import { cn } from "@/lib/utils";
import { BodyPortal } from "@/lib/ui/portal";

export type SheetPosition = "bottom" | "right" | "left";

type SheetProps = {
  open: boolean;
  onClose: () => void;
  title: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
  position?: SheetPosition;
  className?: string;
};

const positionClasses: Record<SheetPosition, { container: string; panel: string; preset: keyof typeof motionPresets }> = {
  bottom: {
    container: "items-end justify-center",
    panel: "w-full max-h-[90dvh] rounded-t-xl border-t border-border",
    preset: "bottomSheet",
  },
  right: {
    container: "justify-end",
    panel: "h-full w-full max-w-md border-l border-border max-md:max-w-full",
    preset: "drawer",
  },
  left: {
    container: "justify-start",
    panel: "h-full w-full max-w-sm border-r border-border max-md:max-w-full",
    preset: "navDrawer",
  },
};

export function Sheet({
  open,
  onClose,
  title,
  children,
  footer,
  position = "bottom",
  className,
}: SheetProps) {
  const reduced = useReducedMotion();
  const panelRef = useRef<HTMLDivElement>(null);
  const cfg = positionClasses[position];
  const preset = motionPresets[cfg.preset];

  useLockBodyScroll(open);
  useFocusTrap(open, panelRef, onClose);

  return (
    <BodyPortal>
      <AnimatePresence>
        {open && (
          <div
            className={cn("fixed inset-0 z-modal flex", cfg.container)}
            role="presentation"
          >
          <m.button
            type="button"
            className="absolute inset-0 bg-overlay-scrim backdrop-blur-[2px]"
            aria-label="Close"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: reduced ? 0.01 : 0.2 }}
            onClick={onClose}
          />
          <m.div
            ref={panelRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby="sheet-title"
            initial={reduced ? false : "hidden"}
            animate={reduced ? undefined : "visible"}
            exit={reduced ? undefined : "exit"}
            variants={preset.variants}
            transition={preset.transition}
            className={cn(
              "relative flex flex-col bg-surface-elevated shadow-premium",
              cfg.panel,
              className,
            )}
          >
            <header className="surface-glass flex shrink-0 items-center justify-between gap-2 border-b border-border-subtle px-4 py-3 pt-safe">
              <h2 id="sheet-title" className="text-base font-semibold text-fg">
                {title}
              </h2>
              <button
                type="button"
                onClick={onClose}
                className="touch-target rounded-md text-fg-muted hover:bg-canvas focus-ring"
                aria-label="Close"
              >
                <X className="h-5 w-5" />
              </button>
            </header>
            <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-4 py-3">
              {children}
            </div>
            {footer && (
              <footer className="flex shrink-0 flex-col-reverse gap-2 border-t border-border px-4 py-3 pb-safe sm:flex-row sm:justify-end max-sm:[&_button]:w-full">
                {footer}
              </footer>
            )}
          </m.div>
        </div>
      )}
    </AnimatePresence>
    </BodyPortal>
  );
}
