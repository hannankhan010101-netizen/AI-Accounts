"use client";

import { AnimatePresence, m } from "framer-motion";
import { useEffect, useId, useRef } from "react";
import { X } from "lucide-react";

import { appPresets } from "@/lib/motion/app-presets";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { useFocusTrap } from "@/lib/responsive/use-focus-trap";
import { useLockBodyScroll } from "@/lib/responsive/use-lock-body-scroll";
import { cn } from "@/lib/utils";
import { BodyPortal } from "@/lib/ui/portal";

interface ModalProps {
  open: boolean;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: "sm" | "md" | "lg";
}

const sizeClass = {
  sm: "max-w-md",
  md: "max-w-2xl",
  lg: "max-w-4xl",
} as const;

export function Modal({ open, title, onClose, children, footer, size = "md" }: ModalProps) {
  const titleId = useId();
  const panelRef = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
  const preset = appPresets.modalEnter;

  useLockBodyScroll(open);
  useFocusTrap(open, panelRef, onClose);

  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  return (
    <BodyPortal>
      <AnimatePresence>
        {open && (
          <div
            className="fixed inset-0 z-modal flex items-end justify-center overflow-hidden p-0 sm:items-center sm:p-4"
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
            aria-labelledby={titleId}
            initial={reduced ? false : "hidden"}
            animate={reduced ? undefined : "visible"}
            exit={reduced ? undefined : "exit"}
            variants={preset.variants}
            transition={preset.transition}
            className={cn(
              "relative flex w-full max-h-[min(90dvh,100%)] flex-col rounded-t-xl bg-surface-elevated shadow-premium sm:max-h-[min(85dvh,100%)] sm:rounded-xl",
              sizeClass[size],
            )}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="surface-glass flex shrink-0 items-center justify-between border-b border-border-subtle px-4 py-3 sm:px-5">
              <h2 id={titleId} className="text-section text-fg">
                {title}
              </h2>
              <button
                type="button"
                onClick={onClose}
                aria-label="Close"
                className="touch-target rounded-md text-fg-muted hover:bg-canvas focus-ring"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-4 py-4 sm:px-5">
              {children}
            </div>
            {footer ? (
              <div className="flex shrink-0 flex-col-reverse gap-2 border-t border-border px-4 py-3 pb-safe sm:flex-row sm:justify-end sm:px-5 max-sm:[&_button]:w-full">
                {footer}
              </div>
            ) : null}
          </m.div>
        </div>
      )}
    </AnimatePresence>
    </BodyPortal>
  );
}
