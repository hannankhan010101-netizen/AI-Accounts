"use client";

import { t } from "@/features/assistant/i18n";
import type { ScreenContext } from "@/lib/assistant/screen-registry";
import type { AiSuggestion } from "@/lib/tour/types";
import { cn } from "@/lib/utils";

type QuickActionsProps = {
  screen: ScreenContext;
  suggestions?: AiSuggestion[];
  onSelect: (text: string) => void;
  className?: string;
};

export function QuickActions({
  screen,
  suggestions = [],
  onSelect,
  className,
}: QuickActionsProps) {
  const chips = [
    ...screen.quickActions.map((a) => ({ label: a.label, text: a.prompt })),
    ...suggestions.slice(0, 2).map((s) => ({
      label: s.title,
      text: s.reason || s.title,
    })),
  ].slice(0, 4);

  if (chips.length === 0) return null;

  return (
    <div className={cn("border-b border-border-subtle/60 bg-surface-muted/30 px-3 py-2 dark:border-border-subtle/30", className)}>
      <p className="mb-1.5 text-[10px] font-medium uppercase tracking-wide text-fg-muted">
        {t("en", "quickActions")}
      </p>
      <div className="flex flex-wrap gap-1.5">
        {chips.map((chip) => (
          <button
            key={chip.label}
            type="button"
            className="rounded-full bg-surface px-2.5 py-1 text-[11px] font-medium text-fg motion-safe-transition hover:bg-surface-accent hover:text-brand-700 focus-ring dark:bg-surface-muted/50 dark:hover:text-brand-200"
            onClick={() => onSelect(chip.text)}
          >
            {chip.label}
          </button>
        ))}
      </div>
    </div>
  );
}
