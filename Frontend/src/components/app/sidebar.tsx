"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { AnimatePresence, m } from "framer-motion";
import { ChevronDown, ChevronRight, PanelLeftClose, PanelLeftOpen, X } from "lucide-react";
import { BrandLogo } from "@/components/brand/brand-logo";
import { cn } from "@/lib/utils";
import { useConfiguredNavGroups } from "@/lib/hooks/use-configured-navigation";
import { expandedGroupsForPath, isNavActive } from "@/lib/navigation/match-active";
import { useShell } from "@/lib/layout/shell-context";
import { tourNavTargetId } from "@/lib/tour/sidebar-navigation";
import {
  clickNavLinkInDom,
  registerTourShellActions,
  unregisterTourShellActions,
} from "@/lib/tour/shell-actions";
import type { NavGroup } from "@/config/navigation";
import { motionPresets } from "@/lib/motion/presets";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { useFocusTrap } from "@/lib/responsive/use-focus-trap";
import { useLockBodyScroll } from "@/lib/responsive/use-lock-body-scroll";
import { useSwipeToClose } from "@/lib/responsive/use-swipe-to-close";

const HOVER_COLLAPSE_MS = 200;
const MotionLink = m.create(Link);

function NavGroupSection({
  group,
  pathname,
  compact,
  open,
  onToggle,
  onRailInteract,
  onNavigate,
}: {
  group: NavGroup;
  pathname: string;
  compact: boolean;
  open: boolean;
  onToggle: () => void;
  onRailInteract?: () => void;
  onNavigate?: () => void;
}) {
  const reduced = useReducedMotion();
  const Icon = group.icon;
  const groupActive = group.items?.some((item) => isNavActive(pathname, item.href)) ?? false;

  const groupPanelId = `nav-group-${group.label.replace(/\s+/g, "-").toLowerCase()}`;

  if (!group.items) {
    const active = group.href ? isNavActive(pathname, group.href) : false;
    return (
      <MotionLink
        href={group.href ?? "#"}
        data-tour={group.href ? tourNavTargetId(group.href) : undefined}
        title={compact ? group.label : undefined}
        onClick={() => {
          if (compact) onRailInteract?.();
          onNavigate?.();
        }}
        whileHover={reduced ? undefined : { x: compact ? 0 : 2 }}
        className={cn(
          "relative flex items-center gap-2 rounded-lg py-2.5 text-fg motion-safe-transition hover:bg-surface-muted",
          compact ? "justify-center px-2" : "px-3",
          active &&
            "bg-brand-600/10 font-medium text-brand-700 dark:bg-brand-400/12 dark:text-brand-200",
          active &&
            "before:absolute before:left-0 before:top-1 before:bottom-1 before:w-0.5 before:rounded-full before:bg-brand-600 dark:before:bg-brand-400 dark:before:shadow-[0_0_8px_color-mix(in_srgb,var(--brand-400)_45%,transparent)]",
        )}
      >
        <Icon className="h-4 w-4 shrink-0" aria-hidden />
        {!compact && <span className="truncate">{group.label}</span>}
        {compact && <span className="sr-only">{group.label}</span>}
      </MotionLink>
    );
  }

  return (
    <div className="mb-0.5">
      <button
        type="button"
        onClick={() => {
          if (compact) onRailInteract?.();
          onToggle();
        }}
        aria-expanded={open}
        aria-controls={groupPanelId}
        title={compact ? group.label : undefined}
        className={cn(
          "relative flex w-full items-center rounded-md py-2 text-fg motion-safe-transition hover:bg-canvas",
          compact ? "justify-center px-2" : "justify-between px-3",
          groupActive &&
            !open &&
            !compact &&
            "font-medium text-brand-700 dark:text-brand-200",
          groupActive &&
            compact &&
            "bg-brand-600/10 text-brand-700 dark:bg-brand-400/12 dark:text-brand-200",
          groupActive &&
            !compact &&
            "before:absolute before:left-0 before:top-1 before:bottom-1 before:w-0.5 before:rounded-full before:bg-brand-600 before:shadow-brand-glow dark:before:bg-brand-400",
        )}
      >
        <span className={cn("flex min-w-0 items-center gap-2", compact && "justify-center")}>
          <Icon className="h-4 w-4 shrink-0" aria-hidden />
          {!compact && <span className="truncate">{group.label}</span>}
          {compact && <span className="sr-only">{group.label}</span>}
        </span>
        {!compact &&
          (open ? (
            <ChevronDown className="h-4 w-4 shrink-0" aria-hidden />
          ) : (
            <ChevronRight className="h-4 w-4 shrink-0" aria-hidden />
          ))}
      </button>
      {open && !compact && (
        <div id={groupPanelId} className="ml-5 mt-0.5 space-y-0.5 pl-2 dark:ml-4">
          {group.items.map((item) => {
            const active = isNavActive(pathname, item.href);
            return (
              <NavItemLink key={item.href} item={item} active={active} onNavigate={onNavigate} />
            );
          })}
        </div>
      )}
    </div>
  );
}

function NavItemLink({
  item,
  active,
  className,
  onNavigate,
}: {
  item: { label: string; href: string; catalogLabel?: string };
  active: boolean;
  className?: string;
  onNavigate?: () => void;
}) {
  const reduced = useReducedMotion();
  const router = useRouter();
  return (
    <MotionLink
      href={item.href}
      data-tour={tourNavTargetId(item.href)}
      title={item.catalogLabel}
      whileHover={reduced ? undefined : { x: 2 }}
      className={cn(
        "rounded-md py-1.5 text-fg-muted motion-safe-transition hover:bg-canvas hover:text-fg",
        className ?? "block px-3",
        active &&
          "bg-brand-600/10 font-medium text-brand-700 dark:bg-brand-400/12 dark:text-brand-200",
      )}
      onMouseEnter={() => router.prefetch(item.href)}
      onClick={onNavigate}
    >
      {item.label}
    </MotionLink>
  );
}

function SidebarNav({
  compact,
  onRailInteract,
  onNavigate,
}: {
  compact: boolean;
  onRailInteract?: () => void;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const { openGroups, setGroupOpen } = useShell();
  const navGroups = useConfiguredNavGroups();

  useEffect(() => {
    const pathOpen = expandedGroupsForPath(pathname, navGroups);
    for (const [label, isOpen] of Object.entries(pathOpen)) {
      if (isOpen && openGroups[label] === undefined) {
        setGroupOpen(label, true);
      }
    }
  }, [pathname, openGroups, setGroupOpen]);

  return (
    <nav
      className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden p-2 text-sm"
      aria-label="Main"
      data-tour="sidebar-nav"
    >
      {navGroups.map((group) => {
        const pathExpanded = expandedGroupsForPath(pathname, navGroups)[group.label];
        const expanded = openGroups[group.label] ?? pathExpanded ?? false;
        return (
          <div key={group.label}>
            <NavGroupSection
              group={group}
              pathname={pathname}
              compact={compact}
              open={expanded}
              onToggle={() => setGroupOpen(group.label, !expanded)}
              onRailInteract={onRailInteract}
              onNavigate={onNavigate}
            />
          </div>
        );
      })}
    </nav>
  );
}

export function Sidebar() {
  const router = useRouter();
  const reduced = useReducedMotion();
  const mobileDrawerRef = useRef<HTMLElement>(null);
  const { sidebarMode, toggleSidebarMode, mobileNavOpen, setMobileNavOpen, setGroupOpen, setSidebarMode } =
    useShell();
  const pinnedCompact = sidebarMode === "compact";
  const [hovered, setHovered] = useState(false);
  const leaveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useLockBodyScroll(mobileNavOpen);
  useFocusTrap(mobileNavOpen, mobileDrawerRef, () => setMobileNavOpen(false));
  const onDrawerDragEnd = useSwipeToClose(() => setMobileNavOpen(false), "left");

  const showExpanded = !pinnedCompact || hovered;
  const navCompact = !showExpanded;

  const clearLeaveTimer = () => {
    if (leaveTimerRef.current) {
      clearTimeout(leaveTimerRef.current);
      leaveTimerRef.current = null;
    }
  };

  const handlePointerEnter = () => {
    clearLeaveTimer();
    if (pinnedCompact) setHovered(true);
  };

  const handlePointerLeave = () => {
    if (!pinnedCompact) return;
    clearLeaveTimer();
    leaveTimerRef.current = setTimeout(() => setHovered(false), HOVER_COLLAPSE_MS);
  };

  useEffect(() => () => clearLeaveTimer(), []);

  useEffect(() => {
    registerTourShellActions({
      ensureSidebarExpanded: () => {
        setSidebarMode("expanded");
        setHovered(true);
      },
      expandNavGroup: (label) => setGroupOpen(label, true),
      clickNavLink: (href) => clickNavLinkInDom(href),
      navigateToHref: (href) => router.push(href),
    });
    return () => unregisterTourShellActions();
  }, [router, setGroupOpen, setSidebarMode, sidebarMode]);

  useEffect(() => {
    if (!mobileNavOpen) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setMobileNavOpen(false);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [mobileNavOpen, setMobileNavOpen]);

  const expandRail = () => {
    clearLeaveTimer();
    setHovered(true);
  };

  const inner = (
    <>
      <div
        className={cn(
          "flex shrink-0 border-b border-border-subtle onboarding-mesh dark:border-border-subtle/60",
          navCompact
            ? "h-[4.25rem] flex-col items-center justify-center gap-0.5 px-1.5 py-2"
            : "h-[3.75rem] flex-row items-center gap-1 px-2.5",
        )}
      >
        <BrandLogo
          variant={navCompact ? "sidebarCompact" : "sidebar"}
          href="/dashboard"
          priority
          className={navCompact ? undefined : "min-w-0 flex-1"}
        />
        <button
          type="button"
          onClick={toggleSidebarMode}
          className={cn(
            "hidden shrink-0 rounded-md text-fg-muted motion-safe-transition",
            "hover:bg-canvas hover:text-fg focus-ring md:inline-flex",
            navCompact ? "p-1" : "p-1.5",
          )}
          aria-label={pinnedCompact ? "Pin sidebar expanded" : "Collapse sidebar to icons"}
        >
          {pinnedCompact ? (
            <PanelLeftOpen className="h-3.5 w-3.5" aria-hidden />
          ) : (
            <PanelLeftClose className="h-4 w-4" aria-hidden />
          )}
        </button>
      </div>
      <SidebarNav
        compact={navCompact}
        onRailInteract={pinnedCompact ? expandRail : undefined}
        onNavigate={() => setMobileNavOpen(false)}
      />
    </>
  );

  return (
    <>
      <div
        className={cn(
          "hidden h-full shrink-0 overflow-hidden md:block",
          "transition-[width] duration-200 ease-out motion-reduce:transition-none",
          showExpanded ? "w-sidebar-expanded" : "w-sidebar-compact",
        )}
        onMouseEnter={handlePointerEnter}
        onMouseLeave={handlePointerLeave}
      >
        <aside
          className="flex h-full w-full flex-col overflow-hidden border-r border-border-subtle bg-surface surface-glass dark:border-r-0 dark:shadow-[4px_0_24px_-8px_rgba(0,0,0,0.45)]"
          aria-label={showExpanded ? "Main navigation" : "Main navigation (collapsed)"}
        >
          {inner}
        </aside>
      </div>

      <AnimatePresence>
        {mobileNavOpen && (
          <div className="fixed inset-0 z-[calc(var(--z-drawer)+1)] md:hidden" role="presentation">
            <m.button
              type="button"
              className="absolute inset-0 bg-overlay-scrim backdrop-blur-[2px]"
              aria-label="Close navigation"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: reduced ? 0.01 : 0.2 }}
              onClick={() => setMobileNavOpen(false)}
            />
            <m.aside
              ref={mobileDrawerRef}
              role="dialog"
              aria-modal="true"
              aria-label="Mobile navigation"
              initial={reduced ? false : "hidden"}
              animate={reduced ? undefined : "visible"}
              exit={reduced ? undefined : "exit"}
              variants={motionPresets.navDrawer.variants}
              transition={motionPresets.navDrawer.transition}
              drag={reduced ? false : "x"}
              dragConstraints={{ left: 0, right: 0 }}
              dragElastic={0.12}
              onDragEnd={onDrawerDragEnd}
              className="surface-glass absolute left-0 top-0 flex h-full w-sidebar-expanded flex-col border-r border-border-subtle pt-safe shadow-premium touch-pan-y"
            >
              <div className="flex h-[3.75rem] shrink-0 items-center justify-between gap-2 border-b border-border px-3">
                <BrandLogo variant="sidebar" href="/dashboard" priority className="min-w-0 flex-1" />
                <button
                  type="button"
                  className="touch-target rounded-md text-fg-muted hover:bg-canvas focus-ring"
                  onClick={() => setMobileNavOpen(false)}
                  aria-label="Close navigation"
                >
                  <X className="h-5 w-5" aria-hidden />
                </button>
              </div>
              <SidebarNav compact={false} onNavigate={() => setMobileNavOpen(false)} />
            </m.aside>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
