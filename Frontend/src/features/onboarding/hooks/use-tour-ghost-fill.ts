"use client";

import { useEffect, useRef, useState } from "react";
import type { FieldValues, UseFormReturn } from "react-hook-form";

import {
  GHOST_FILL_RECIPES,
  resolveGhostValue,
  type GhostFillContext,
} from "@/lib/tour/ghost-fill-recipes";
import { useTour } from "@/lib/tour/tour-context";

const GHOST_CLASS = "tour-ghost-filled";

type UseTourGhostFillOptions<T extends FieldValues> = {
  form: UseFormReturn<T>;
  context: GhostFillContext;
};

/**
 * When an interactive demo step sets `ghostFill`, animates sample values into the form.
 * Does not submit — pair with `useTourDemoSandbox()` to disable save.
 */
export function useTourGhostFill<T extends FieldValues>({
  form,
  context,
}: UseTourGhostFillOptions<T>) {
  const { currentStep, running, isDemoSandbox } = useTour();
  const [filling, setFilling] = useState(false);
  const appliedRef = useRef<string | null>(null);

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
        if (!value) return;
        form.setValue(entry.path as never, value as never, {
          shouldDirty: false,
          shouldValidate: false,
        });
        const el = document.querySelector<HTMLElement>(
          `[name="${entry.path}"], [id="${entry.path}"]`,
        );
        el?.classList.add(GHOST_CLASS);
        window.setTimeout(() => el?.classList.remove(GHOST_CLASS), 1200);
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
    form,
    context.customerIds.join(","),
    context.supplierIds.join(","),
    context.bankAccountIds.join(","),
    context.productCodes.join(","),
  ]);

  return { filling, active };
}

export function useTourDemoSandbox(): boolean {
  const { isDemoSandbox } = useTour();
  return isDemoSandbox;
}
