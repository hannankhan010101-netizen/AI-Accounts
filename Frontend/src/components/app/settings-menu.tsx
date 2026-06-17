"use client";

import Link from "next/link";
import { X } from "lucide-react";
import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

import { settingsColumns } from "@/config/settings-menu";
import { clearTokens } from "@/lib/auth/storage";
import { useFocusTrap } from "@/lib/responsive/use-focus-trap";
import { useLockBodyScroll } from "@/lib/responsive/use-lock-body-scroll";
import { BodyPortal } from "@/lib/ui/portal";

interface SettingsMenuProps {
  open: boolean;
  onClose: () => void;
}

/**
 * Settings mega-menu modal — catalog §12.1.
 * Multi-column link grid with right-rail session controls.
 */
export function SettingsMenu({ open, onClose }: SettingsMenuProps) {
  const router = useRouter();
  const panelRef = useRef<HTMLDivElement>(null);

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

  if (!open) return null;

  function signOut() {
    clearTokens();
    onClose();
    router.push("/login");
  }

  return (
    <BodyPortal>
      <div
        className="fixed inset-0 z-modal flex items-start justify-center overflow-y-auto bg-overlay-scrim p-4 pb-safe pt-[max(1.5rem,env(safe-area-inset-top))] backdrop-blur-[2px] sm:p-6"
        role="presentation"
        onMouseDown={(e) => {
          if (e.target === e.currentTarget) onClose();
        }}
      >
        <div
          ref={panelRef}
          role="dialog"
          aria-modal="true"
          aria-labelledby="settings-menu-title"
          className="relative my-auto w-full max-w-6xl rounded-xl bg-surface-elevated shadow-premium"
        >
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="absolute right-3 top-3 touch-target rounded-md text-fg-muted hover:bg-canvas focus-ring"
          >
            <X className="h-5 w-5" />
          </button>

          <h2 id="settings-menu-title" className="sr-only">
            Settings catalog
          </h2>

          <div className="grid grid-cols-1 gap-6 p-6 md:grid-cols-4">
            {settingsColumns.map((col) => (
              <div key={col.title}>
                <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-brand-700 dark:text-brand-300">
                  {col.title}
                </h3>
                <div className="space-y-3">
                  {col.groups.map((group) => (
                    <div key={group.label}>
                      <div className="mb-1 text-xs font-semibold text-fg-muted">{group.label}</div>
                      <ul className="space-y-0.5">
                        {group.links.map((link) => (
                          <li key={link.href}>
                            <Link
                              href={link.href}
                              onClick={onClose}
                              className="block rounded-md px-2 py-1.5 text-sm text-fg hover:bg-canvas focus-ring"
                            >
                              {link.label}
                            </Link>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            <div className="border-t border-border pt-6 md:border-l md:border-t-0 md:pl-6 md:pt-0">
              <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-brand-700 dark:text-brand-300">
                Session
              </h3>
              <ul className="space-y-1 text-sm">
                <li>
                  <Link
                    href="/profile"
                    onClick={onClose}
                    className="block rounded-md px-2 py-1.5 hover:bg-canvas focus-ring"
                  >
                    Profile
                  </Link>
                </li>
                <li>
                  <Link
                    href="/profile/change-password"
                    onClick={onClose}
                    className="block rounded-md px-2 py-1.5 hover:bg-canvas focus-ring"
                  >
                    Change Password
                  </Link>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={signOut}
                    className="block w-full rounded-md px-2 py-1.5 text-left text-status-danger hover:bg-status-danger/10 focus-ring"
                  >
                    Logout
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </BodyPortal>
  );
}
