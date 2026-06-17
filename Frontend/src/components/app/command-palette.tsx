"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { FilePlus, Navigation, Settings, Sparkles } from "lucide-react";

import {
  AI_COMMAND_PREFIX,
  TOUR_COMMAND_PREFIX,
  type CommandItem,
  type CommandKind,
} from "@/config/command-registry";
import { useCopilotStore } from "@/stores/assistant/copilot-store";
import { useTour } from "@/lib/tour/tour-context";
import { useCompany } from "@/lib/auth/company-context";
import { buildCommandList, filterAllCommands } from "@/lib/commands/report-commands";
import { fetchReportFavorites, loadReportFavorites } from "@/lib/reports/favorites";
import { useLockBodyScroll } from "@/lib/responsive/use-lock-body-scroll";
import { cn } from "@/lib/utils";

const kindIcon: Record<CommandKind, typeof Navigation> = {
  navigate: Navigation,
  create: FilePlus,
  settings: Settings,
  tour: Sparkles,
  ai: Sparkles,
};

interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
}

export function CommandPalette({ open, onClose }: CommandPaletteProps) {
  const router = useRouter();
  const { companyId } = useCompany();
  const { startTour, setAiPanelOpen } = useTour();
  const setCopilotOpen = useCopilotStore((s) => s.setOpen);
  const setCopilotMode = useCopilotStore((s) => s.setMode);
  const setDraft = useCopilotStore((s) => s.setDraft);
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);
  const [favorites, setFavorites] = useState<Set<string>>(() => loadReportFavorites(companyId));

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    void fetchReportFavorites(companyId).then((set) => {
      if (!cancelled) setFavorites(set);
    });
    return () => {
      cancelled = true;
    };
  }, [companyId, open]);

  const allCommands = useMemo(() => buildCommandList(favorites), [favorites]);
  const results = useMemo(() => filterAllCommands(query, favorites), [query, favorites]);

  const run = useCallback(
    (item: CommandItem) => {
      onClose();
      setQuery("");
      setActiveIndex(0);
      if (item.kind === "tour" && item.href.startsWith(TOUR_COMMAND_PREFIX)) {
        const action = item.href.slice(TOUR_COMMAND_PREFIX.length);
        if (action === "assistant") {
          setAiPanelOpen(true);
          return;
        }
        startTour(action);
        return;
      }
      if (item.kind === "ai" && item.href.startsWith(AI_COMMAND_PREFIX)) {
        const action = item.href.slice(AI_COMMAND_PREFIX.length);
        setCopilotMode(action === "invoice" || action === "reconcile" ? "erp" : "erp");
        if (action === "invoice") {
          setDraft("How do I create or find a sales invoice?");
        } else if (action === "reconcile") {
          setDraft("How do I reconcile my bank account?");
        } else if (action === "search") {
          setDraft("");
        }
        setCopilotOpen(true);
        if (action === "search") {
          setTimeout(() => {
            document.querySelector<HTMLInputElement>('[aria-label="Ask anything about this screen…"]')?.focus();
          }, 100);
        }
        return;
      }
      router.push(item.href);
    },
    [onClose, router, startTour, setAiPanelOpen, setCopilotOpen, setCopilotMode, setDraft],
  );

  useEffect(() => {
    if (!open) return;
    setQuery("");
    setActiveIndex(0);
    const t = window.setTimeout(() => inputRef.current?.focus(), 0);
    return () => window.clearTimeout(t);
  }, [open]);

  useEffect(() => {
    setActiveIndex((i) => Math.min(i, Math.max(0, results.length - 1)));
  }, [results.length]);

  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
        return;
      }
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setActiveIndex((i) => Math.min(i + 1, results.length - 1));
      }
      if (e.key === "ArrowUp") {
        e.preventDefault();
        setActiveIndex((i) => Math.max(i - 1, 0));
      }
      if (e.key === "Enter" && results[activeIndex]) {
        e.preventDefault();
        run(results[activeIndex]);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose, results, activeIndex, run]);

  useLockBodyScroll(open);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[60] flex items-end justify-center bg-overlay-scrim p-0 backdrop-blur-[2px] sm:items-start sm:p-4 sm:pt-[12vh]"
      role="presentation"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Command palette"
        className={cn(
          "flex max-h-[min(90dvh,100%)] w-full flex-col overflow-hidden border border-border-subtle bg-surface-elevated shadow-premium transition-transform duration-fast ease-out motion-reduce:transition-none",
          "rounded-t-xl sm:max-w-xl sm:rounded-lg",
        )}
      >
        <div className="border-b border-border px-4 py-3">
          <input
            ref={inputRef}
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search pages and actions…"
            aria-label="Search commands"
            className="w-full bg-transparent text-base text-fg outline-none placeholder:text-fg-muted sm:text-sm"
            autoComplete="off"
          />
          <p className="mt-1 text-xs text-fg-muted">
            <kbd className="rounded border border-border px-1">↑↓</kbd> navigate{" "}
            <kbd className="rounded border border-border px-1">↵</kbd> open{" "}
            <kbd className="rounded border border-border px-1">esc</kbd> close
          </p>
        </div>
        <ul className="min-h-0 flex-1 overflow-y-auto overscroll-contain py-1 sm:max-h-[min(360px,50vh)]" role="listbox">
          {results.length === 0 && (
            <li className="px-4 py-6 text-center text-sm text-fg-muted">No matching commands</li>
          )}
          {results.map((item, index) => {
            const Icon = kindIcon[item.kind];
            return (
              <li key={item.id} role="option" aria-selected={index === activeIndex}>
                <button
                  type="button"
                  className={cn(
                    "flex w-full items-center gap-3 px-4 py-2 text-left text-sm",
                    index === activeIndex
                      ? "bg-brand-50 text-brand-700 dark:bg-brand-100/12 dark:text-brand-300"
                      : "text-fg hover:bg-canvas/80",
                  )}
                  onMouseEnter={() => setActiveIndex(index)}
                  onClick={() => run(item)}
                >
                  <Icon className="h-4 w-4 shrink-0 opacity-70" aria-hidden />
                  <span className="flex-1 font-medium">{item.label}</span>
                  {item.kind === "create" && (
                    <span className="text-xs text-fg-muted">Create</span>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
        {!query && (
          <div className="border-t border-border px-4 py-2 text-xs text-fg-muted">
            {allCommands.length} commands
            {favorites.size > 0 ? ` · ${favorites.size} starred report${favorites.size === 1 ? "" : "s"}` : ""}
            {" · try "}
            &quot;invoice&quot;, &quot;tour&quot;, &quot;learn&quot;
          </div>
        )}
      </div>
    </div>
  );
}

/** Global Cmd+K / Ctrl+K listener */
export function useCommandPalette() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((v) => !v);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return {
    open,
    setOpen,
    openPalette: () => setOpen(true),
    closePalette: () => setOpen(false),
  };
}
