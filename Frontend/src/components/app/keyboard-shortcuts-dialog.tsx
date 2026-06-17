"use client";

import { useEffect, useState } from "react";
import { X } from "lucide-react";

import { keyboardShortcuts, shortcutGroups } from "@/config/keyboard-shortcuts";
import { BodyPortal } from "@/lib/ui/portal";
import { cn } from "@/lib/utils";

function ShortcutKeys({ keys }: { keys: string[] }) {
  return (
    <span className="inline-flex flex-wrap gap-1">
      {keys.map((key, i) => (
        <span key={`${key}-${i}`} className="inline-flex items-center gap-1">
          {i > 0 && <span className="text-fg-muted">+</span>}
          <kbd className="rounded border border-border bg-canvas px-1.5 py-0.5 font-mono text-xs text-fg">
            {key}
          </kbd>
        </span>
      ))}
    </span>
  );
}

interface KeyboardShortcutsDialogProps {
  open: boolean;
  onClose: () => void;
}

export function KeyboardShortcutsDialog({ open, onClose }: KeyboardShortcutsDialogProps) {
  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  const byId = Object.fromEntries(keyboardShortcuts.map((s) => [s.id, s]));

  return (
    <BodyPortal>
      <div
        className="fixed inset-0 z-command flex items-center justify-center bg-overlay-scrim p-4 backdrop-blur-[2px]"
        role="presentation"
        onMouseDown={(e) => {
          if (e.target === e.currentTarget) onClose();
        }}
      >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="shortcuts-title"
        className="max-h-[min(80vh,560px)] w-full max-w-lg overflow-hidden rounded-lg border border-border bg-surface-elevated shadow-xl"
      >
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <h2 id="shortcuts-title" className="text-base font-semibold text-fg">
            Keyboard shortcuts
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1.5 text-fg-muted hover:bg-canvas focus-ring"
            aria-label="Close shortcuts"
          >
            <X className="h-4 w-4" aria-hidden />
          </button>
        </div>
        <div className="overflow-y-auto px-4 py-3">
          {shortcutGroups.map((group) => (
            <section key={group.title} className="mb-4 last:mb-0">
              <h3 className="mb-2 text-xs font-medium uppercase tracking-wide text-fg-muted">
                {group.title}
              </h3>
              <ul className="space-y-2">
                {group.ids.map((id) => {
                  const item = byId[id];
                  if (!item) return null;
                  return (
                    <li
                      key={id}
                      className={cn(
                        "flex flex-wrap items-center justify-between gap-2 text-sm text-fg",
                      )}
                    >
                      <span>{item.description}</span>
                      <ShortcutKeys keys={item.keys} />
                    </li>
                  );
                })}
              </ul>
            </section>
          ))}
        </div>
        <p className="border-t border-border px-4 py-2 text-xs text-fg-muted">
          Press <kbd className="rounded border border-border px-1">?</kbd> anywhere outside a field
          to open this panel.
        </p>
      </div>
      </div>
    </BodyPortal>
  );
}

function isEditableTarget(target: EventTarget | null): boolean {
  if (!target || !(target instanceof HTMLElement)) return false;
  const tag = target.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return true;
  return target.isContentEditable;
}

/** Global `?` listener — skips when typing in inputs. */
export function useKeyboardShortcutsHelp() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key !== "?" || e.ctrlKey || e.metaKey || e.altKey) return;
      if (isEditableTarget(e.target)) return;
      e.preventDefault();
      setOpen((v) => !v);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return {
    open,
    toggleHelp: () => setOpen((v) => !v),
    openHelp: () => setOpen(true),
    closeHelp: () => setOpen(false),
  };
}