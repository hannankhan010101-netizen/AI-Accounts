"use client";

import type { AppRouterInstance } from "next/dist/shared/lib/app-router-context.shared-runtime";

import { isAllowedRoute, resolveScreenContext } from "@/lib/assistant/screen-registry";

const HIGHLIGHT_CLASS = "fa-assistant-highlight";
const HIGHLIGHT_STYLE_ID = "fa-assistant-highlight-style";

function ensureHighlightStyle() {
  if (typeof document === "undefined") return;
  if (document.getElementById(HIGHLIGHT_STYLE_ID)) return;
  const style = document.createElement("style");
  style.id = HIGHLIGHT_STYLE_ID;
  style.textContent = `
    .${HIGHLIGHT_CLASS} {
      outline: 2px solid var(--brand-600) !important;
      outline-offset: 2px;
      border-radius: 4px;
      transition: outline 0.2s ease;
    }
  `;
  document.head.appendChild(style);
}

export type ClientToolDeps = {
  router: AppRouterInstance;
  pathname: string;
  startTour: (id: string) => void;
  openModal?: (id: string) => void;
};

export async function executeClientTool(
  name: string,
  args: Record<string, unknown>,
  deps: ClientToolDeps,
): Promise<Record<string, unknown>> {
  switch (name) {
    case "navigate": {
      const route = String(args.route ?? "");
      if (!isAllowedRoute(route)) {
        return { ok: false, error: `Route not allowed: ${route}` };
      }
      deps.router.push(route);
      return { ok: true, route };
    }
    case "openModal": {
      const id = String(args.id ?? "");
      if (id === "keyboard-shortcuts") {
        window.dispatchEvent(new CustomEvent("fa:open-keyboard-shortcuts"));
        return { ok: true, id };
      }
      if (deps.openModal) {
        deps.openModal(id);
        return { ok: true, id };
      }
      return { ok: false, error: `Unknown modal: ${id}` };
    }
    case "highlightElement": {
      const selector = String(args.selector ?? "");
      if (!selector || typeof document === "undefined") {
        return { ok: false, error: "Invalid selector" };
      }
      ensureHighlightStyle();
      const el = document.querySelector(selector);
      if (!el) return { ok: false, error: `Element not found: ${selector}` };
      el.classList.add(HIGHLIGHT_CLASS);
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      window.setTimeout(() => el.classList.remove(HIGHLIGHT_CLASS), 4000);
      return { ok: true, selector };
    }
    case "startTour": {
      const id = String(args.id ?? "");
      deps.startTour(id);
      return { ok: true, tourId: id };
    }
    case "explainScreen": {
      const pathname = String(args.pathname ?? deps.pathname);
      const ctx = resolveScreenContext(pathname);
      return {
        ok: true,
        pathname,
        title: ctx.title,
        description: ctx.description,
        module: ctx.module,
        tourIds: ctx.tourIds,
      };
    }
    default:
      return { ok: false, error: `Not a client tool: ${name}` };
  }
}
