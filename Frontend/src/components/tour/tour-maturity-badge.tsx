"use client";

import { completedTourCount, maturityLevelForScore } from "@/lib/tour/maturity";
import { getTourEntry } from "@/lib/tour/progress-store";
import { useTour } from "@/lib/tour/tour-context";

export function TourMaturityBadge() {
  const { progress, machine, running } = useTour();
  const score = progress.maturityScore ?? 0;
  const completed = completedTourCount(progress);

  if (running && (machine === "running" || machine === "waiting_target")) {
    return (
      <div
        className="inline-flex items-center gap-2 rounded-full border border-brand-600/30 bg-brand-600/10 px-3 py-1 text-xs dark:border-brand-100/30"
        aria-live="polite"
      >
        <span className="font-semibold text-brand-700 dark:text-brand-100">Tour in progress</span>
        <span className="text-fg-muted">
          Step {running.stepIndex + 1} of {running.steps.length}
        </span>
      </div>
    );
  }

  const pausedCore = getTourEntry(progress, "onboard.core", 1);
  if (pausedCore.status === "in_progress") {
    return (
      <div
        className="inline-flex items-center gap-2 rounded-full border border-brand-600/30 bg-brand-600/10 px-3 py-1 text-xs dark:border-brand-100/30"
        aria-live="polite"
      >
        <span className="font-semibold text-brand-700 dark:text-brand-100">Welcome tour paused</span>
        <span className="text-fg-muted">
          Step {pausedCore.stepIndex + 1} of 5 — use Continue tour on the dashboard
        </span>
      </div>
    );
  }

  if (score <= 0 && completed === 0) return null;

  const level = maturityLevelForScore(score);

  return (
    <div
      className="inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1 text-xs"
      title={`${completed} tour(s) completed · maturity ${score}%`}
    >
      <span className="font-semibold text-brand-700 dark:text-brand-100">{level.label}</span>
      <span className="text-fg-muted">
        {completed} tour{completed === 1 ? "" : "s"} · {score}%
      </span>
    </div>
  );
}
