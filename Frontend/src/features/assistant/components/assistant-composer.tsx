"use client";

import { Send, Square } from "lucide-react";
import { useCallback } from "react";

import { Button } from "@/components/ui/button";
import { t } from "@/features/assistant/i18n";
import { cn } from "@/lib/utils";

type AssistantComposerProps = {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
  isBusy?: boolean;
  onStop?: () => void;
};

export function AssistantComposer({
  value,
  onChange,
  onSubmit,
  disabled,
  isBusy,
  onStop,
}: AssistantComposerProps) {
  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (!value.trim() || disabled) return;
      onSubmit();
    },
    [disabled, onSubmit, value],
  );

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!value.trim() || disabled) return;
      onSubmit();
    }
  };

  return (
    <form
      className="shrink-0 border-t border-border-subtle/60 bg-surface/95 p-3 dark:border-border-subtle/30"
      onSubmit={handleSubmit}
    >
      <div className="flex items-end gap-2 rounded-xl bg-surface-muted/50 p-1.5 dark:bg-surface-muted/40">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t("en", "placeholder")}
          aria-label={t("en", "placeholder")}
          disabled={disabled}
          rows={1}
          className={cn(
            "max-h-24 min-h-[2.25rem] flex-1 resize-none bg-transparent px-2 py-1.5 text-sm text-fg",
            "placeholder:text-fg-muted focus:outline-none disabled:opacity-60",
          )}
        />
        {isBusy && onStop ? (
          <Button
            type="button"
            size="icon"
            variant="outline"
            onClick={onStop}
            aria-label={t("en", "stop")}
            className="h-9 w-9 shrink-0 rounded-lg"
          >
            <Square className="h-3.5 w-3.5 fill-current" aria-hidden />
          </Button>
        ) : (
          <Button
            type="submit"
            size="icon"
            variant="primary"
            disabled={!value.trim() || disabled}
            aria-label={t("en", "send")}
            className="h-9 w-9 shrink-0 rounded-lg"
          >
            <Send className="h-3.5 w-3.5" aria-hidden />
          </Button>
        )}
      </div>
      <p className="sr-only">{t("en", "composerHint")}</p>
    </form>
  );
}
