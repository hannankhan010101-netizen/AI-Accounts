import { MOBILE_MEDIA_QUERY } from "@/lib/responsive/constants";
import { navGroupForHref, pathnameMatchesRoute, tourNavTargetId } from "@/lib/tour/sidebar-navigation";
import { getTourShellActions } from "@/lib/tour/shell-actions";
import {
  prepareNavTourTargetVisibility,
  queryTourTarget,
  scrollTargetIntoView,
} from "@/lib/tour/target-resolver";
import { tourTargetSelector } from "@/lib/tour/target-selector";
import type { TourDefinition, TourStep, TourStepAction, TourTargetSpec } from "@/lib/tour/types";
import { isInteractiveTour } from "@/lib/tour/types";

const NAV_LINK_POLL_MS = 80;
const SIDEBAR_SETTLE_MS = 520;
const POST_ROUTE_SETTLE_MS = 350;

function isVisible(el: HTMLElement): boolean {
  const rect = el.getBoundingClientRect();
  if (rect.width < 2 || rect.height < 2) return false;
  const style = window.getComputedStyle(el);
  return style.display !== "none" && style.visibility !== "hidden" && style.opacity !== "0";
}

function delay(ms: number): Promise<void> {
  return new Promise((r) => window.setTimeout(r, ms));
}

function nextFrame(): Promise<void> {
  return new Promise((r) => requestAnimationFrame(() => r()));
}

/** Wait until pathname matches (polls window.location). */
export function waitForRoute(href: string, timeoutMs = 14000): Promise<boolean> {
  if (pathnameMatchesRoute(window.location.pathname, href)) {
    return Promise.resolve(true);
  }
  const deadline = Date.now() + timeoutMs;
  return new Promise((resolve) => {
    function tick() {
      if (pathnameMatchesRoute(window.location.pathname, href)) {
        resolve(true);
        return;
      }
      if (Date.now() >= deadline) {
        resolve(false);
        return;
      }
      window.setTimeout(tick, 60);
    }
    tick();
  });
}

export function waitForTourTargetVisible(
  spec: TourTargetSpec,
  timeoutMs = 12000,
): Promise<HTMLElement | null> {
  const deadline = Date.now() + timeoutMs;
  return new Promise((resolve) => {
    function tick() {
      const el = queryTourTarget(spec);
      if (el) {
        resolve(el);
        return;
      }
      if (Date.now() >= deadline) {
        resolve(null);
        return;
      }
      window.setTimeout(tick, 100);
    }
    tick();
  });
}

async function waitForNavLinkVisible(href: string, timeoutMs = 5000): Promise<HTMLElement | null> {
  const sel = `[data-tour="${tourNavTargetId(href)}"]`;
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const el = document.querySelector<HTMLElement>(sel);
    if (el && isVisible(el)) return el;
    await delay(NAV_LINK_POLL_MS);
  }
  return null;
}

/** Expand sidebar + nav group, then click link or fall back to router. */
export async function prepareSidebarAndNavigate(
  href: string,
  push: (path: string) => void,
  groupLabel?: string,
): Promise<void> {
  const shell = getTourShellActions();
  const isMobile =
    typeof window !== "undefined" && window.matchMedia(MOBILE_MEDIA_QUERY).matches;
  if (isMobile) {
    shell.openMobileNav?.();
    await delay(380);
  } else {
    shell.closeMobileNav?.();
    shell.ensureSidebarExpanded?.();
  }
  await nextFrame();
  await nextFrame();
  await delay(SIDEBAR_SETTLE_MS);

  const group = groupLabel ?? navGroupForHref(href);
  if (group) shell.expandNavGroup?.(group);
  await delay(200);

  const link = await waitForNavLinkVisible(href, 9000);
  if (link) {
    link.scrollIntoView({ block: "nearest", inline: "nearest", behavior: "smooth" });
    await delay(120);
    link.click();
    return;
  }

  shell.navigateToHref?.(href);
  push(href);
}

export async function executeTourAction(
  action: TourStepAction,
  push: (href: string) => void,
): Promise<void> {
  const shell = getTourShellActions();

  switch (action.type) {
    case "navigate":
      shell.ensureSidebarExpanded?.();
      await delay(120);
      push(action.href);
      return;
    case "sidebarNavigate":
      await prepareSidebarAndNavigate(action.href, push, action.groupLabel);
      return;
    case "click": {
      const el = await waitForTourTargetVisible({ kind: "tour", id: action.tourTarget }, 10000);
      if (el) {
        scrollTargetIntoView(el, action.tourTarget);
        await delay(200);
        el.click();
      }
      return;
    }
    case "userConfirm":
    case "none":
      return;
    default:
      return;
  }
}

export function actionHref(action: TourStepAction | null | undefined): string | null {
  if (!action) return null;
  if (action.type === "navigate" || action.type === "sidebarNavigate") return action.href;
  return null;
}

export function resolveEnterAction(def: TourDefinition, step: TourStep): TourStepAction | null {
  if (step.enterAction) return step.enterAction;
  if (step.autoRunEnter === false) return null;
  if (def.type === "demo" || def.type === "workflow") {
    return step.enterAction ?? null;
  }
  if (isInteractiveTour(def) && step.autoRunEnter) return step.enterAction ?? null;
  return null;
}

/** After navigation + target ready, advance without user clicking Next. */
export function shouldAutoContinue(def: TourDefinition, step: TourStep): boolean {
  if (step.autoContinue === false) return false;
  if (def.type === "demo") {
    if (step.autoContinue === true) return true;
    if (step.enterAction) return true;
    if (step.autoAdvanceMs) return true;
    return step.target.kind === "panel";
  }
  if (def.type === "workflow" || isInteractiveTour(def)) {
    return (
      step.autoContinue === true ||
      Boolean(step.enterAction) ||
      Boolean(step.autoAdvanceMs)
    );
  }
  return false;
}

export function shouldAutoAdvance(def: TourDefinition, step: TourStep): boolean {
  return (
    (def.type === "demo" || isInteractiveTour(def)) &&
    typeof step.autoAdvanceMs === "number" &&
    step.autoAdvanceMs > 0
  );
}

export function resolveInitialStepIndex(
  def: TourDefinition,
  steps: TourStep[],
  fromStep: number,
  pathname: string,
): number {
  if (fromStep > 0) return Math.min(fromStep, steps.length - 1);

  if (def.type === "demo" || def.type === "workflow") {
    for (let i = 0; i < steps.length; i++) {
      const href = actionHref(resolveEnterAction(def, steps[i]) ?? steps[i].action);
      if (href && pathnameMatchesRoute(pathname, href)) {
        return i;
      }
    }
    const firstAction = steps.findIndex(
      (s) => s.enterAction || s.action?.type === "navigate" || s.action?.type === "sidebarNavigate",
    );
    if (def.type === "demo" && firstAction > 0) {
      return firstAction;
    }
  }

  return 0;
}

export type RunStepWorkflowInput = {
  def: TourDefinition;
  step: TourStep;
  push: (href: string) => void;
  onTargetReady: (spec: TourTargetSpec) => void;
  onNavigating?: (active: boolean) => void;
};

/** Run enter action, wait for route/target, then notify tour context. */
export async function runStepWorkflow(input: RunStepWorkflowInput): Promise<void> {
  const { def, step, push, onTargetReady, onNavigating } = input;
  const enter = resolveEnterAction(def, step);

  if (step.target.kind === "panel") {
    onTargetReady(step.target);
    return;
  }

  onNavigating?.(Boolean(enter));

  try {
    if (enter) {
      await executeTourAction(enter, push);
      const href = actionHref(enter);
      if (href) {
        let routed = await waitForRoute(href, 12000);
        if (!routed) {
          push(href);
          routed = await waitForRoute(href, 8000);
        }
        if (routed) await delay(POST_ROUTE_SETTLE_MS);
      } else {
        await delay(300);
      }
    }

    const targetId = step.target.kind === "tour" ? step.target.id : undefined;
    if (targetId) {
      await prepareNavTourTargetVisibility(targetId);
    }

    const el = await waitForTourTargetVisible(step.target, 14000);
    if (el) {
      scrollTargetIntoView(el, targetId);
      await delay(enter ? 200 : 0);
    }
    onTargetReady(step.target);
  } finally {
    onNavigating?.(false);
  }
}

export function validateStep(step: TourStep, pathname: string): boolean {
  const v = step.validation;
  if (!v || v.type === "none") return true;
  if (v.type === "routeMatch") {
    return pathnameMatchesRoute(pathname, v.pathname);
  }
  if (v.type === "elementVisible") {
    return Boolean(queryTourTarget({ kind: "tour", id: v.tourTarget }));
  }
  return true;
}

export function waitForValidation(
  step: TourStep,
  pathname: string,
  timeoutMs = 10000,
): Promise<boolean> {
  const deadline = Date.now() + (timeoutMs ?? 10000);
  return new Promise((resolve) => {
    function tick() {
      const path = window.location.pathname;
      if (validateStep(step, path)) {
        resolve(true);
        return;
      }
      if (Date.now() >= deadline) {
        resolve(false);
        return;
      }
      window.setTimeout(tick, 100);
    }
    tick();
  });
}
