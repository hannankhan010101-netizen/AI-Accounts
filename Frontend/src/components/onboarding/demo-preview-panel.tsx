"use client";

import { m } from "framer-motion";
import { FileSpreadsheet } from "lucide-react";

import { getDemoPreview } from "@/lib/tour/demo-sample-data";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";

type DemoPreviewPanelProps = {
  previewId?: string;
};

export function DemoPreviewPanel({ previewId }: DemoPreviewPanelProps) {
  const reduced = useReducedMotion();
  const preview = getDemoPreview(previewId);
  if (!preview) return null;

  return (
    <m.div
      initial={reduced ? false : { opacity: 0, y: 6 }}
      animate={reduced ? undefined : { opacity: 1, y: 0 }}
      className="rounded-xl border border-brand-600/15 bg-gradient-to-br from-brand-600/5 to-transparent p-3 dark:from-brand-100/5"
    >
      <div className="flex items-start gap-2">
        <FileSpreadsheet
          className="mt-0.5 h-4 w-4 shrink-0 text-brand-600 dark:text-brand-100"
          aria-hidden
        />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-xs font-semibold text-fg">{preview.headline}</p>
            {preview.badge && (
              <span className="rounded-full bg-canvas px-2 py-0.5 text-[10px] font-medium text-fg-muted">
                {preview.badge}
              </span>
            )}
          </div>
          <ul className="mt-2 space-y-1">
            {preview.lines.map((line) => (
              <li key={line} className="text-xs leading-relaxed text-fg-muted">
                {line}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </m.div>
  );
}
