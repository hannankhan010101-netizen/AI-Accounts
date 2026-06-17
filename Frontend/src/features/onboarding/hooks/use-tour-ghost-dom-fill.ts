"use client";

import { useEffect, useRef, useState } from "react";

import {
  GHOST_FILL_RECIPES,
  resolveGhostValue,
  type GhostFillContext,
} from "@/lib/tour/ghost-fill-recipes";
import { useTour } from "@/lib/tour/tour-context";

const GHOST_CLASS = "tour-ghost-filled";

type UseTourGhostDomFillOptions = {
  /** Keys must match `path` in ghost-fill recipe entries. */
  setters: Record<string, (value: string) => void>;
  context: GhostFillContext;
  /** Optional selectors to flash after fill: path → CSS selector */
  highlightSelectors?: Record<string, string>;
};

/** Ghost fill for pages that use useState instead of react-hook-form. */
export function useTourGhostDomFill({
  setters,
  context,
  highlightSelectors = {},
}: UseTourGhostDomFillOptions) {
  const { currentStep, running, isDemoSandbox } = useTour();
  const [filling, setFilling] = useState(false);
  const appliedRef = useRef<string | null>(null);
  const settersRef = useRef(setters);
  settersRef.current = setters;

  const recipeId = currentStep?.ghostFill;
  const active =
    isDemoSandbox &&
    Boolean(running) &&
    Boolean(recipeId) &&
    Boolean(GHOST_FILL_RECIPES[recipeId ?? ""]);

  useEffect(() => {
    if (!active || !recipeId) {
      setFilling(false);
      return;
    }

    const key = `${running?.definition.id}:${running?.stepIndex}:${recipeId}`;
    if (appliedRef.current === key) return;

    const recipe = GHOST_FILL_RECIPES[recipeId];
    if (!recipe) return;

    appliedRef.current = key;
    setFilling(true);
    const timers: number[] = [];

    for (const entry of recipe.fields) {
      const t = window.setTimeout(() => {
        const value = resolveGhostValue(entry.resolve, context);
        const apply = settersRef.current[entry.path];
        if (value && apply) apply(value);
        const sel = highlightSelectors[entry.path];
        if (sel) {
          const el = document.querySelector<HTMLElement>(sel);
          el?.classList.add(GHOST_CLASS);
          window.setTimeout(() => el?.classList.remove(GHOST_CLASS), 1200);
        }
      }, entry.delayMs);
      timers.push(t);
    }

    const done = window.setTimeout(() => setFilling(false), 1600);
    timers.push(done);

    return () => {
      for (const id of timers) window.clearTimeout(id);
    };
  }, [
    active,
    recipeId,
    running?.definition.id,
    running?.stepIndex,
    context.customerIds.join(","),
    context.supplierIds.join(","),
    context.bankAccountIds.join(","),
    context.productCodes.join(","),
    highlightSelectors,
  ]);

  return { filling, active };
}
