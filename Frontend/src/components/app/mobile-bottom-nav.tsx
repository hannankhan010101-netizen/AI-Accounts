"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Banknote, Boxes, Home, MoreHorizontal, ShoppingCart, Truck } from "lucide-react";

import { useShell } from "@/lib/layout/shell-context";
import { useMyPermissions } from "@/lib/rbac/use-my-permissions";
import { cn } from "@/lib/utils";

const tabs = [
  { label: "Home", href: "/dashboard", icon: Home, match: (p: string) => p === "/dashboard" },
  {
    label: "Sell",
    href: "/sales/invoices",
    icon: ShoppingCart,
    moduleCode: "sales",
    match: (p: string) => p.startsWith("/sales"),
  },
  {
    label: "Buy",
    href: "/purchases/bills",
    icon: Truck,
    moduleCode: "purchases",
    match: (p: string) => p.startsWith("/purchases"),
  },
  {
    label: "Stock",
    href: "/inventory/products",
    icon: Boxes,
    moduleCode: "inventory",
    match: (p: string) => p.startsWith("/inventory"),
  },
  {
    label: "Insights",
    href: "/reports",
    icon: BarChart3,
    moduleCode: "financial",
    match: (p: string) => p.startsWith("/reports"),
  },
  {
    label: "Money",
    href: "/bank/balances",
    icon: Banknote,
    moduleCode: "bank",
    match: (p: string) => p.startsWith("/bank"),
    moreOnly: true,
  },
] as const;

function tabVisible(
  tab: (typeof tabs)[number],
  modules: { moduleCode: string; canAccess?: boolean; sidebarVisible?: boolean }[],
): boolean {
  if (!("moduleCode" in tab) || !tab.moduleCode) return true;
  const row = modules.find((m) => m.moduleCode === tab.moduleCode);
  if (!row) return true;
  return Boolean(row.canAccess && (row.sidebarVisible ?? true));
}

export function MobileBottomNav() {
  const pathname = usePathname();
  const { setMobileNavOpen, mobileNavOpen } = useShell();
  const { data } = useMyPermissions();
  const modules = data?.result?.modules ?? [];
  const primaryTabs = tabs.filter((tab) => !("moreOnly" in tab && tab.moreOnly));
  const visibleTabs = primaryTabs.filter((tab) => tabVisible(tab, modules));

  const moreActive =
    pathname.startsWith("/settings") ||
    pathname.startsWith("/admin") ||
    pathname.startsWith("/bank") ||
    tabs.some((tab) => "moreOnly" in tab && tab.moreOnly && tab.match(pathname));

  return (
    <nav
      className={cn(
        "fixed inset-x-0 bottom-0 z-30 border-t border-border-subtle surface-glass pb-safe dark:border-border-subtle/40 md:hidden",
        mobileNavOpen && "pointer-events-none opacity-0",
      )}
      aria-label="Primary navigation"
      aria-hidden={mobileNavOpen}
      style={{ height: "calc(var(--bottom-nav-height) + env(safe-area-inset-bottom, 0px))" }}
    >
      <ul
        className="grid h-[var(--bottom-nav-height)]"
        style={{ gridTemplateColumns: `repeat(${visibleTabs.length + 1}, minmax(0, 1fr))` }}
      >
        {visibleTabs.map((tab) => {
          const active = tab.match(pathname);
          const Icon = tab.icon;
          return (
            <li key={tab.label}>
              <Link
                href={tab.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "touch-target mx-1 flex h-full flex-col items-center justify-center gap-0.5 rounded-lg px-1 text-[10px] font-medium leading-tight motion-safe-transition",
                  active
                    ? "bg-brand-600/10 text-brand-700 shadow-xs dark:bg-brand-400/12 dark:text-brand-200"
                    : "text-fg-muted hover:text-fg",
                )}
              >
                <Icon className="h-5 w-5 shrink-0" aria-hidden />
                <span className="max-w-full truncate">{tab.label}</span>
              </Link>
            </li>
          );
        })}
        <li>
          <button
            type="button"
            onClick={() => setMobileNavOpen(true)}
            aria-pressed={moreActive}
            aria-label="More navigation"
            className={cn(
              "touch-target flex h-full w-full flex-col items-center justify-center gap-0.5 rounded-lg px-1 text-[10px] font-medium leading-tight motion-safe-transition",
              moreActive
                ? "bg-brand-600/10 text-brand-700 shadow-xs dark:bg-brand-400/12 dark:text-brand-200"
                : "text-fg-muted hover:text-fg",
            )}
          >
            <MoreHorizontal className="h-5 w-5 shrink-0" aria-hidden />
            <span>More</span>
          </button>
        </li>
      </ul>
    </nav>
  );
}
