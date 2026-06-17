"use client";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";

import { useRouter } from "next/navigation";
import { usePathname } from "next/navigation";
import {
  ChevronDown,
  Clock,
  LifeBuoy,
  ListTodo,
  Menu,
  Moon,
  MoreVertical,
  Search,
  Settings as SettingsIcon,
  Sun,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";

import Link from "next/link";

import { BrandMark } from "@/components/brand/brand-mark";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CommandPalette, useCommandPalette } from "@/components/app/command-palette";
import {
  KeyboardShortcutsDialog,
  useKeyboardShortcutsHelp,
} from "@/components/app/keyboard-shortcuts-dialog";
import { useTheme } from "@/components/providers/theme-provider";
import { clearTokens } from "@/lib/auth/storage";
import { useCompany } from "@/lib/auth/company-context";
import { useShell } from "@/lib/layout/shell-context";
import {
  registerTourShellActions,
  unregisterTourShellActions,
} from "@/lib/tour/shell-actions";
import { SettingsMenu } from "./settings-menu";
import { UserMenu } from "./user-menu";
import { tasksApi } from "@/lib/api/tenant";

export function TopBar() {
  const router = useRouter();
  const pathname = usePathname();
  const { companyId, companies, selectCompany } = useCompany();
  const [companyMenuOpen, setCompanyMenuOpen] = useState(false);
  const [overflowOpen, setOverflowOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [switching, setSwitching] = useState(false);
  const companyMenuRef = useRef<HTMLDivElement>(null);
  const { open: paletteOpen, openPalette, closePalette } = useCommandPalette();
  const { open: shortcutsOpen, toggleHelp, closeHelp: closeShortcuts } = useKeyboardShortcutsHelp();
  const { setMobileNavOpen } = useShell();
  const { mode: themeMode, resolvedDark, cycleMode } = useTheme();

  const themeLabel =
    themeMode === "dark"
      ? "Dark theme"
      : themeMode === "light"
        ? "Light theme"
        : resolvedDark
          ? "System theme (dark)"
          : "System theme (light)";

  useEffect(() => {
    registerTourShellActions({
      openCommandPalette: openPalette,
      closeCommandPalette: closePalette,
      openShortcutsHelp: toggleHelp,
      openMobileNav: () => setMobileNavOpen(true),
      closeMobileNav: () => setMobileNavOpen(false),
      closeCompanyMenu: () => setCompanyMenuOpen(false),
    });
    return () => unregisterTourShellActions();
  }, [openPalette, closePalette, toggleHelp, setMobileNavOpen]);

  useEffect(() => {
    function onOpenShortcuts() {
      toggleHelp();
    }
    window.addEventListener("fa:open-keyboard-shortcuts", onOpenShortcuts);
    return () => window.removeEventListener("fa:open-keyboard-shortcuts", onOpenShortcuts);
  }, [toggleHelp]);

  useEffect(() => {
    setCompanyMenuOpen(false);
    setOverflowOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!companyMenuOpen) return;
    function onDoc(e: MouseEvent) {
      if (companyMenuRef.current && !companyMenuRef.current.contains(e.target as Node)) {
        setCompanyMenuOpen(false);
      }
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setCompanyMenuOpen(false);
    }
    document.addEventListener("mousedown", onDoc);
    window.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDoc);
      window.removeEventListener("keydown", onKey);
    };
  }, [companyMenuOpen]);

  const current = companyId ? companies.find((c) => c.id === companyId) : undefined;

  const tasksQuery = useTenantReferenceQuery(["my-tasks", "count", companyId], () => tasksApi.list(), { enabled: Boolean(companyId) });
  const taskCount = tasksQuery.data?.result.length ?? 0;

  async function switchTo(id: string) {
    if (!id || id === companyId) {
      setCompanyMenuOpen(false);
      return;
    }
    setSwitching(true);
    try {
      await selectCompany(id);
      router.refresh();
    } finally {
      setSwitching(false);
      setCompanyMenuOpen(false);
    }
  }

  function signOut() {
    clearTokens();
    router.push("/login");
  }

  return (
    <>
      <header className="surface-glass sticky top-0 z-30 flex h-[var(--top-bar-height)] shrink-0 items-center justify-between gap-2 border-b border-border-subtle px-safe pt-safe backdrop-blur-md dark:border-border-subtle/50 sm:gap-3 sm:px-4">
        <div className="flex min-w-0 flex-1 items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="touch-target md:hidden"
            data-tour="mobile-menu"
            onClick={() => setMobileNavOpen(true)}
            aria-label="Open navigation menu"
          >
            <Menu className="h-5 w-5" />
          </Button>
          <Link
            href="/dashboard"
            className="flex shrink-0 items-center justify-center rounded-md p-1 hover:opacity-90 focus-ring md:hidden"
            aria-label="Dashboard home"
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600/10 ring-1 ring-brand-600/20 dark:bg-brand-100/12 dark:ring-brand-400/25">
              <BrandMark size={20} className="h-5 w-5" />
            </span>
          </Link>
          <div className="relative" ref={companyMenuRef}>
            <Card variant="glass" className="inline-flex overflow-hidden border-transparent p-0 shadow-none dark:bg-surface-muted/40">
              <button
                type="button"
                data-tour="company-switcher"
                disabled={switching}
                onClick={() => setCompanyMenuOpen((s) => !s)}
                className="flex max-w-[220px] items-center gap-2 px-3 py-1.5 text-sm hover:bg-surface-muted disabled:opacity-60 sm:max-w-xs"
                aria-haspopup="listbox"
                aria-expanded={companyMenuOpen}
              >
                <span className="truncate font-medium">
                  {switching
                    ? "Switching…"
                    : (current?.name ?? (companies.length ? "Select company" : "No company"))}
                </span>
                <ChevronDown className="h-4 w-4 shrink-0 text-fg-muted" aria-hidden />
              </button>
            </Card>
            {companyMenuOpen && (
              <div
                className="absolute left-0 z-40 mt-1 w-64 rounded-md border border-border bg-surface-elevated py-1 shadow-lg"
                role="listbox"
              >
                {companies.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    role="option"
                    aria-selected={c.id === companyId}
                    onClick={() => switchTo(c.id)}
                    className={`block w-full px-3 py-2 text-left text-sm hover:bg-canvas ${
                      c.id === companyId
                        ? "bg-brand-600/12 font-medium text-brand-700 dark:bg-brand-100/10 dark:text-brand-100"
                        : ""
                    }`}
                  >
                    {c.name}
                  </button>
                ))}
                {companies.length === 0 && (
                  <div className="px-3 py-2 text-sm text-fg-muted">No companies yet</div>
                )}
              </div>
            )}
          </div>

          <div className="hidden min-w-0 flex-1 sm:flex sm:max-w-md" data-tour="command-palette">
            <button
              type="button"
              onClick={openPalette}
              className="flex w-full items-center gap-2 rounded-lg border border-border bg-canvas/80 px-3 py-1.5 text-sm text-fg-muted shadow-[inset_0_1px_2px_rgba(26,31,22,0.06)] hover:bg-surface dark:border-transparent dark:bg-surface-muted/50 dark:shadow-[inset_0_1px_0_rgba(255,255,255,0.04)] dark:hover:bg-surface-muted/70"
              aria-label="Open command palette"
            >
              <Search className="h-4 w-4 shrink-0" aria-hidden />
              <span className="truncate">Search or jump to…</span>
              <kbd className="ml-auto hidden rounded border border-border bg-surface px-1.5 text-xs lg:inline">
                Ctrl K
              </kbd>
            </button>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-0.5 sm:gap-1">
          <div className="sm:hidden" data-tour="command-palette">
            <Button variant="ghost" size="icon" className="touch-target" onClick={openPalette} aria-label="Search">
              <Search className="h-5 w-5" />
            </Button>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="touch-target max-sm:hidden sm:inline-flex"
            onClick={cycleMode}
            aria-label={themeLabel}
            title={themeLabel}
          >
            {resolvedDark ? (
              <Moon className="h-5 w-5" aria-hidden />
            ) : (
              <Sun className="h-5 w-5" aria-hidden />
            )}
          </Button>
          <div className="relative max-sm:hidden sm:contents">
            <Button variant="ghost" size="sm" className="relative" asChild>
              <Link href="/my-tasks" data-tour="my-tasks">
                <ListTodo className="mr-1.5 h-4 w-4" />
                <span className="hidden sm:inline">My tasks</span>
                {taskCount > 0 && (
                  <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-brand px-1 text-[10px] font-semibold text-on-brand">
                    {taskCount > 99 ? "99+" : taskCount}
                  </span>
                )}
              </Link>
            </Button>
            <Button variant="ghost" size="icon" className="max-sm:hidden" asChild>
              <Link href="/settings/user-log" title="Activity log" data-tour="activity-log">
                <Clock className="h-5 w-5" />
                <span className="sr-only">Activity log</span>
              </Link>
            </Button>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/support" data-tour="support">
                <LifeBuoy className="mr-1.5 h-4 w-4" />
                <span className="hidden sm:inline">Support</span>
              </Link>
            </Button>
            <Button variant="ghost" size="sm" onClick={() => router.push("/admin")}>
              <SettingsIcon className="mr-1.5 h-4 w-4" />
              <span className="hidden sm:inline">Admin</span>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleHelp}
              title="Keyboard shortcuts (?)"
              aria-label="Keyboard shortcuts"
              className="hidden sm:inline-flex"
            >
              <span className="font-mono text-xs">?</span>
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setSettingsOpen(true)} title="Full settings catalog">
              Settings
            </Button>
            <UserMenu onOpenSettings={() => setSettingsOpen(true)} />
          </div>
          <div className="relative sm:hidden">
            <Button
              variant="ghost"
              size="icon"
              className="touch-target"
              aria-label="More actions"
              aria-expanded={overflowOpen}
              onClick={() => setOverflowOpen((o) => !o)}
            >
              <MoreVertical className="h-5 w-5" />
            </Button>
            {overflowOpen && (
              <>
                <button
                  type="button"
                  className="fixed inset-0 z-drawer bg-overlay-scrim/40"
                  aria-label="Close menu"
                  onClick={() => setOverflowOpen(false)}
                />
                <div className="absolute right-0 z-[calc(var(--z-drawer)+1)] mt-1 w-48 rounded-md border border-border bg-surface-elevated py-1 shadow-lg">
                  <button
                    type="button"
                    className="flex w-full items-center gap-2 px-3 py-2.5 text-left text-sm hover:bg-canvas"
                    onClick={() => {
                      setOverflowOpen(false);
                      cycleMode();
                    }}
                  >
                    {resolvedDark ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
                    {themeLabel}
                  </button>
                  <Link
                    href="/my-tasks"
                    className="flex w-full px-3 py-2.5 text-left text-sm hover:bg-canvas"
                    onClick={() => setOverflowOpen(false)}
                  >
                    My tasks
                  </Link>
                  <Link
                    href="/settings/user-log"
                    className="flex w-full px-3 py-2.5 text-left text-sm hover:bg-canvas"
                    onClick={() => setOverflowOpen(false)}
                  >
                    Activity log
                  </Link>
                  <Link
                    href="/support"
                    className="flex w-full px-3 py-2.5 text-left text-sm hover:bg-canvas"
                    onClick={() => setOverflowOpen(false)}
                  >
                    Support
                  </Link>
                  <button
                    type="button"
                    className="flex w-full px-3 py-2.5 text-left text-sm hover:bg-canvas"
                    onClick={() => {
                      setOverflowOpen(false);
                      router.push("/admin");
                    }}
                  >
                    Admin
                  </button>
                  <button
                    type="button"
                    className="flex w-full px-3 py-2.5 text-left text-sm hover:bg-canvas"
                    onClick={() => {
                      setOverflowOpen(false);
                      setSettingsOpen(true);
                    }}
                  >
                    Settings
                  </button>
                  <Link
                    href="/profile"
                    className="flex w-full px-3 py-2.5 text-left text-sm hover:bg-canvas"
                    onClick={() => setOverflowOpen(false)}
                  >
                    Profile
                  </Link>
                  <button
                    type="button"
                    className="flex w-full px-3 py-2.5 text-left text-sm hover:bg-canvas"
                    onClick={() => {
                      setOverflowOpen(false);
                      signOut();
                    }}
                  >
                    Sign out
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </header>

      <CommandPalette open={paletteOpen} onClose={closePalette} />
      <KeyboardShortcutsDialog open={shortcutsOpen} onClose={closeShortcuts} />
      <SettingsMenu open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </>
  );
}
