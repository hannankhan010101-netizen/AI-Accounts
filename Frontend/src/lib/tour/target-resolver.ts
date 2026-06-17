import { MOBILE_MEDIA_QUERY } from "@/lib/responsive/constants";
import { scrollGridTourRow } from "@/lib/tour/grid-tour-bridge";
import { getTourShellActions } from "@/lib/tour/shell-actions";
import {
  hrefFromNavTourTargetId,
  isNavTourTargetId,
  navGroupForHref,
} from "@/lib/tour/sidebar-navigation";
import { tourTargetSelector } from "@/lib/tour/target-selector";

import type { TourTargetSpec } from "@/lib/tour/types";



const MAX_RETRIES = 6;

const RETRY_MS = [80, 120, 200, 400, 600, 800];



const VIEWPORT_MARGIN = 12;

const SPOTLIGHT_PAD = 10;



function isTourTargetVisible(el: HTMLElement): boolean {

  const rect = el.getBoundingClientRect();

  if (rect.width < 2 || rect.height < 2) return false;

  const style = window.getComputedStyle(el);

  return style.display !== "none" && style.visibility !== "hidden" && style.opacity !== "0";

}



export function queryTourTarget(spec: TourTargetSpec): HTMLElement | null {

  if (spec.kind === "panel") return null;

  const sel = tourTargetSelector(spec);

  if (!sel) return null;

  const nodes = document.querySelectorAll<HTMLElement>(sel);

  for (const el of nodes) {

    if (isTourTargetVisible(el)) return el;

  }

  if (

    spec.kind === "tour" &&

    spec.id === "sidebar-nav" &&

    typeof window !== "undefined" &&

    window.matchMedia(MOBILE_MEDIA_QUERY).matches

  ) {

    return queryTourTarget({ kind: "tour", id: "mobile-menu" });

  }

  return null;

}

function delay(ms: number): Promise<void> {
  return new Promise((r) => window.setTimeout(r, ms));
}

/** Expand sidebar / nav group so `nav-*` tour links are visible before measuring. */
export async function prepareNavTourTargetVisibility(tourTargetId: string): Promise<void> {
  const shell = getTourShellActions();
  const isMobile =
    typeof window !== "undefined" && window.matchMedia(MOBILE_MEDIA_QUERY).matches;

  if (isMobile) {
    shell.openMobileNav?.();
    await delay(360);
    return;
  }

  shell.closeMobileNav?.();
  shell.ensureSidebarExpanded?.();
  await delay(480);

  if (tourTargetId === "sidebar-nav") return;

  const href = hrefFromNavTourTargetId(tourTargetId);
  if (!href) return;
  const group = navGroupForHref(href);
  if (group) shell.expandNavGroup?.(group);
  await delay(280);
}



export function waitForTourTarget(

  spec: TourTargetSpec,

  onFound: (el: HTMLElement | null) => void,

): () => void {

  if (spec.kind === "panel") {

    onFound(null);

    return () => {};

  }



  if (spec.kind === "grid" && spec.rowIndex !== undefined) {

    scrollGridTourRow(spec.id, spec.rowIndex);

  }



  let cancelled = false;

  let attempt = 0;



  function tryOnce() {

    if (cancelled) return;

    const el = queryTourTarget(spec);

    if (el) {

      onFound(el);

      return;

    }

    attempt += 1;

    if (attempt >= MAX_RETRIES) {

      onFound(null);

      return;

    }

    if (spec.kind === "grid" && spec.rowIndex !== undefined && attempt === 2) {

      scrollGridTourRow(spec.id, spec.rowIndex);

    }

    window.setTimeout(tryOnce, RETRY_MS[attempt - 1] ?? 800);

  }



  tryOnce();

  return () => {

    cancelled = true;

  };

}



export type TargetRect = {

  top: number;

  left: number;

  width: number;

  height: number;

};



/** Raw viewport bounds of the element (no padding). */

export function measureTarget(el: HTMLElement | null): TargetRect | null {

  if (!el) return null;

  const r = el.getBoundingClientRect();

  return {

    top: r.top,

    left: r.left,

    width: r.width,

    height: r.height,

  };

}



/** Padded spotlight hole, clamped inside the viewport so header controls stay visible. */

export function toSpotlightRect(rect: TargetRect): TargetRect {

  if (typeof window === "undefined") {

    return {

      top: rect.top - SPOTLIGHT_PAD,

      left: rect.left - SPOTLIGHT_PAD,

      width: rect.width + SPOTLIGHT_PAD * 2,

      height: rect.height + SPOTLIGHT_PAD * 2,

    };

  }



  const vw = window.innerWidth;

  const vh = window.innerHeight;

  let top = rect.top - SPOTLIGHT_PAD;

  let left = rect.left - SPOTLIGHT_PAD;

  let width = rect.width + SPOTLIGHT_PAD * 2;

  let height = rect.height + SPOTLIGHT_PAD * 2;



  if (top < VIEWPORT_MARGIN) {

    height += VIEWPORT_MARGIN - top;

    top = VIEWPORT_MARGIN;

  }

  if (left < VIEWPORT_MARGIN) {

    width += VIEWPORT_MARGIN - left;

    left = VIEWPORT_MARGIN;

  }

  if (top + height > vh - VIEWPORT_MARGIN) {

    height = Math.max(rect.height, vh - VIEWPORT_MARGIN - top);

  }

  if (left + width > vw - VIEWPORT_MARGIN) {

    width = Math.max(rect.width, vw - VIEWPORT_MARGIN - left);

  }



  return { top, left, width, height };

}



export function isHeaderTourTarget(rect: TargetRect): boolean {

  return rect.top < 120 && rect.height < 80;

}



/** Large targets push bottom-placed tooltips off-screen. */

export function isOversizedTourTarget(rect: TargetRect, tourTargetId?: string): boolean {

  if (tourTargetId === "sidebar-nav") return false;

  if (typeof window === "undefined") return false;

  const vh = window.innerHeight;

  const vw = window.innerWidth;

  return rect.height > vh * 0.45 || rect.width > vw * 0.45;

}



const HEADER_TOUR_TARGETS = new Set([

  "company-switcher",

  "command-palette",

  "mobile-menu",

  "tour-button",

]);



/** Prefer the visible control inside a tour wrapper (e.g. company dropdown button). */

export function resolveTourMeasureElement(

  el: HTMLElement,

  tourTargetId?: string,

): HTMLElement {

  if (tourTargetId === "company-switcher" || tourTargetId === "command-palette") {

    const btn = el.querySelector<HTMLElement>("button:not([role='option'])");

    if (btn && isTourTargetVisible(btn)) return btn;

  }

  if (tourTargetId === "tour-button") {

    const btn = el.querySelector<HTMLElement>("button");

    if (btn && isTourTargetVisible(btn)) return btn;

  }

  if (tourTargetId === "sidebar-nav") {
    const nav = el.closest("nav") ?? el;
    const candidates = nav.querySelectorAll<HTMLElement>(
      "a[data-tour], button[type='button']",
    );
    for (const node of candidates) {
      if (isTourTargetVisible(node)) return node;
    }
  }

  if (tourTargetId && isNavTourTargetId(tourTargetId)) {
    const link = el.matches("a[data-tour]")
      ? el
      : el.querySelector<HTMLElement>(`[data-tour="${tourTargetId}"]`);
    if (link && isTourTargetVisible(link)) return link;
  }

  return el;

}



export function scrollTargetIntoView(el: HTMLElement | null, tourTargetId?: string): void {

  if (!el) return;

  // Top bar is outside the main scroll region; scrolling here clips header targets.

  if (tourTargetId && HEADER_TOUR_TARGETS.has(tourTargetId)) {

    if (window.scrollY !== 0) window.scrollTo({ top: 0, left: 0, behavior: "auto" });

    return;

  }



  const r = el.getBoundingClientRect();

  const offscreen =

    r.top < 0 ||

    r.bottom > window.innerHeight ||

    r.left < 0 ||

    r.right > window.innerWidth;

  if (!offscreen) return;



  el.scrollIntoView({

    block: "nearest",

    inline: "nearest",

    behavior: "auto",

  });

}


