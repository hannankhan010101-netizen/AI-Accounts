"use client";

import { m } from "framer-motion";

import { AssistantAvatar } from "@/features/assistant/components/assistant-avatar";
import { t } from "@/features/assistant/i18n";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { cn } from "@/lib/utils";

type AssistantThinkingProps = {
  label?: string;
  className?: string;
};

export function AssistantThinking({ label, className }: AssistantThinkingProps) {
  const reduced = useReducedMotion();
  const text = label ?? t("en", "thinking");

  return (
    <m.div
      initial={reduced ? false : { opacity: 0, y: 4 }}
      animate={reduced ? undefined : { opacity: 1, y: 0 }}
      exit={reduced ? undefined : { opacity: 0 }}
      transition={{ duration: 0.12 }}
      className={cn("flex items-center gap-2", className)}
      role="status"
      aria-live="polite"
      aria-label={text}
    >
      <AssistantAvatar role="assistant" pulse />
      <div className="flex items-center gap-1 rounded-2xl rounded-bl-md bg-surface-muted/80 px-3 py-2 dark:bg-surface-muted/50">
        <span className="sr-only">{text}</span>
        {[0, 1, 2].map((i) => (
          <m.span
            key={i}
            className="h-1.5 w-1.5 rounded-full bg-brand-500 dark:bg-brand-400"
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{
              duration: 0.55,
              repeat: Infinity,
              delay: i * 0.1,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>
    </m.div>
  );
}

function formatToolLabel(name: string): string {
  return name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function AssistantToolThinking({ toolName }: { toolName: string }) {
  return (
    <AssistantThinking
      label={t("en", "workingOnTool").replace("{tool}", formatToolLabel(toolName))}
    />
  );
}
