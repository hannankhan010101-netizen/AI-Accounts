"use client";

import { m } from "framer-motion";
import { FlaskConical } from "lucide-react";

import { useReducedMotion } from "@/lib/motion/use-reduced-motion";

type DemoSandboxBannerProps = {
  filling?: boolean;
};

export function DemoSandboxBanner({ filling }: DemoSandboxBannerProps) {
  const reduced = useReducedMotion();

  return (
    <m.div
      role="status"
      initial={reduced ? false : { opacity: 0, y: -4 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-4 flex items-center gap-2 rounded-lg border border-brand-600/20 bg-brand-600/5 px-3 py-2 text-sm text-brand-800 dark:text-brand-100"
    >
      <FlaskConical className="h-4 w-4 shrink-0" aria-hidden />
      <span>
        {filling
          ? "Filling a sample document for you… nothing will be saved."
          : "Demo sandbox — explore freely. Save is disabled until you finish the guide."}
      </span>
    </m.div>
  );
}
