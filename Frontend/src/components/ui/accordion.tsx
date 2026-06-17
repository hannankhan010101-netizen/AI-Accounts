"use client";

import { AnimatePresence, m } from "framer-motion";
import { ChevronDown, ChevronRight } from "lucide-react";
import { useState, type ReactNode } from "react";

import { useReducedMotion } from "@/lib/motion/use-reduced-motion";

interface AccordionItemProps {
  title: string;
  defaultOpen?: boolean;
  children: ReactNode;
}

export function AccordionItem({ title, defaultOpen, children }: AccordionItemProps) {
  const [open, setOpen] = useState(!!defaultOpen);
  const reduced = useReducedMotion();

  return (
    <div className="border-b border-border-subtle last:border-b-0">
      <button
        type="button"
        onClick={() => setOpen((s) => !s)}
        className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-medium text-fg motion-safe-transition hover:bg-surface-muted"
      >
        <span>{title}</span>
        {open ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <m.div
            initial={reduced ? false : { height: 0, opacity: 0 }}
            animate={reduced ? undefined : { height: "auto", opacity: 1 }}
            exit={reduced ? undefined : { height: 0, opacity: 0 }}
            transition={{ duration: reduced ? 0.01 : 0.22, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 pt-1">{children}</div>
          </m.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function Accordion({ children }: { children: ReactNode }) {
  return <div className="surface-elevated overflow-hidden rounded-xl">{children}</div>;
}
