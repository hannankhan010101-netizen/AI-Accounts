"use client";

import { useState } from "react";
import Link from "next/link";
import { useMutation } from "@tanstack/react-query";
import { Bot, Compass, Keyboard, Mail, Megaphone, Search, Sparkles } from "lucide-react";

import { LearningHubPanel } from "@/components/onboarding/learning-hub-panel";
import { Button } from "@/components/ui/button";
import { tourApi } from "@/lib/api/tour";
import { filterTourForContext } from "@/lib/tour/filters";
import {
  getTourDefinition,
  listToursForPersona,
  listDemoTours,
  listWorkflowTours,
  preloadTour,
} from "@/lib/tour/registry";
import { useTourUIStore } from "@/stores/onboarding/tour-ui-store";
import { getTourShellActions } from "@/lib/tour/shell-actions";
import { getTourEntry } from "@/lib/tour/progress-store";
import type { PersonaId } from "@/lib/tour/types";
import { useTour } from "@/lib/tour/tour-context";
import { cn } from "@/lib/utils";

const PERSONA_LABEL: Record<PersonaId, string> = {
  admin: "admins",
  accountant: "accounting teams",
  sales: "sales teams",
  inventory_manager: "inventory teams",
  procurement: "procurement",
  cfo: "finance leaders",
  viewer: "viewers",
  general: "your role",
};

const itemClass =
  "flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm transition-colors hover:bg-canvas/80 focus-ring";

interface TourMenuProps {
  onClose: () => void;
}

export function TourMenu({ onClose }: TourMenuProps) {
  const {
    progress,
    continueTour,
    startTour,
    suggestedTourId,
    pageTourIds,
    running,
    machine,
    persona,
    permissions,
    unreadReleaseCount,
    setAiPanelOpen,
    setMenuOpen,
    updatePreferences,
  } = useTour();
  const [digestMsg, setDigestMsg] = useState<string | null>(null);
  const digestMut = useMutation({
    mutationFn: () => tourApi.postDigestEmail(),
    onSuccess: (res) => setDigestMsg(res.result.message),
    onError: (err) =>
      setDigestMsg(err instanceof Error ? err.message : "Could not send email"),
  });
  const emailDigestOn = progress.preferences?.emailDigestEnabled ?? false;

  const moreTours = listToursForPersona(persona)
    .filter((t) => t.type !== "workflow")
    .filter((t) => t.id !== "onboard.core" && t.id !== suggestedTourId)
    .filter(
      (t) =>
        filterTourForContext(t, { persona, permissions, progress }) !== null,
    )
    .slice(0, 3);

  const practiceMode = useTourUIStore((s) => s.practiceMode);
  const setPracticeMode = useTourUIStore((s) => s.setPracticeMode);

  const demoTours = listDemoTours()
    .filter(
      (t) =>
        filterTourForContext(t, { persona, permissions, progress }) !== null,
    );

  const workflowTours = listWorkflowTours()
    .filter((t) => t.id !== suggestedTourId)
    .filter(
      (t) =>
        filterTourForContext(t, { persona, permissions, progress }) !== null,
    )
    .slice(0, 6);

  const active = running?.definition;
  const continueEntry = active
    ? getTourEntry(progress, active.id, active.version)
    : progress.lastActiveTourId
      ? getTourEntry(
          progress,
          progress.lastActiveTourId,
          getTourDefinition(progress.lastActiveTourId)?.version ?? 1,
        )
      : null;

  const continueId =
    machine === "running" || machine === "waiting_target" || machine === "paused"
      ? active?.id
      : Object.entries(progress.tours).find(([, e]) => e.status === "in_progress")?.[0] ??
        progress.lastActiveTourId;

  const continueDef = continueId ? getTourDefinition(continueId) : null;
  const inProgressSteps =
    continueId && continueEntry
      ? `${continueEntry.stepIndex + 1}/${continueDef?.steps.length ?? "?"}`
      : null;

  function runTour(tourId: string) {
    void preloadTour(tourId);
    startTour(tourId);
    onClose();
  }

  return (
    <LearningHubPanel
      title="Guides & workflows"
      subtitle="Short, role-aware walkthroughs — never blocks your work."
      personaLabel={PERSONA_LABEL[persona]}
    >
      {continueDef &&
        (continueEntry?.status === "in_progress" ||
          machine === "running" ||
          machine === "waiting_target") && (
        <button
          type="button"
          role="menuitem"
          className={cn(itemClass, "flex-col items-start")}
          onClick={() => {
            continueTour();
            onClose();
          }}
        >
          <span className="font-medium text-fg">Continue: {continueDef.title}</span>
          {inProgressSteps && (
            <span className="text-xs text-fg-muted">Step {inProgressSteps}</span>
          )}
        </button>
      )}

      <button
        type="button"
        role="menuitem"
        className={itemClass}
        onMouseEnter={() => suggestedTourId && void preloadTour(suggestedTourId)}
        onClick={() => suggestedTourId && runTour(suggestedTourId)}
      >
        <Compass className="h-4 w-4 shrink-0 text-brand-600 dark:text-brand-100" />
        <span>
          <span className="font-medium text-fg">Tour this page</span>
          <span className="block text-xs text-fg-muted">
            {(suggestedTourId && getTourDefinition(suggestedTourId)?.title) ??
              suggestedTourId ??
              "Welcome tour"}
          </span>
        </span>
      </button>

      {pageTourIds[0] !== "onboard.core" && (
        <button
          type="button"
          role="menuitem"
          className={itemClass}
          onClick={() => runTour("onboard.core")}
        >
          <Sparkles className="h-4 w-4 shrink-0" />
          <span className="font-medium">Welcome tour</span>
        </button>
      )}

      <label className="mx-2 mb-2 flex cursor-pointer items-center gap-2 rounded-lg border border-border/80 bg-canvas/50 px-3 py-2.5 text-sm">
        <input
          type="checkbox"
          checked={practiceMode}
          onChange={(e) => setPracticeMode(e.target.checked)}
          className="rounded border-border"
        />
        <span className="text-fg">
          <span className="font-medium">Practice mode</span>
          <span className="block text-xs text-fg-muted">
            Click targets yourself — safe sandbox, no saves required
          </span>
        </span>
      </label>

      {demoTours.length > 0 && (
        <>
          <p className="px-2 py-2 text-[10px] font-semibold uppercase tracking-widest text-fg-muted">
            Interactive demos
          </p>
          {demoTours.map((t) => {
            const entry = progress.tours[t.id];
            const done = entry?.status === "completed";
            return (
              <button
                key={t.id}
                type="button"
                role="menuitem"
                className={itemClass}
                onMouseEnter={() => void preloadTour(t.id)}
                onClick={() => runTour(t.id)}
              >
                <Sparkles className="h-4 w-4 shrink-0 text-brand-600 dark:text-brand-100" />
                <span>
                  <span className="font-medium text-fg">
                    {t.title}
                    {done ? " ✓" : ""}
                  </span>
                  {t.metadata.tagline && (
                    <span className="block text-xs text-fg-muted">{t.metadata.tagline}</span>
                  )}
                </span>
              </button>
            );
          })}
        </>
      )}

      {workflowTours.length > 0 && (
        <>
          <p className="px-2 py-2 text-[10px] font-semibold uppercase tracking-widest text-fg-muted">
            Workflows
          </p>
          {workflowTours.map((t) => {
            const entry = progress.tours[t.id];
            const done = entry?.status === "completed";
            return (
              <button
                key={t.id}
                type="button"
                role="menuitem"
                className={itemClass}
                onMouseEnter={() => void preloadTour(t.id)}
                onClick={() => runTour(t.id)}
              >
                <span className="font-medium text-fg">
                  {t.title}
                  {done ? " ✓" : ""}
                </span>
              </button>
            );
          })}
        </>
      )}

      {moreTours.map((t) => {
        const entry = progress.tours[t.id];
        const done = entry?.status === "completed";
        return (
          <button
            key={t.id}
            type="button"
            role="menuitem"
            className={itemClass}
            onMouseEnter={() => void preloadTour(t.id)}
            onClick={() => runTour(t.id)}
          >
            <span className="font-medium text-fg">
              {t.title}
              {done ? " ✓" : ""}
            </span>
          </button>
        );
      })}

      <Link
        href="/dashboard"
        role="menuitem"
        className={itemClass}
        onClick={onClose}
      >
        <Megaphone className="h-4 w-4 shrink-0" />
        <span className="flex-1 font-medium">What&apos;s New</span>
        {unreadReleaseCount > 0 && (
          <span className="rounded-full bg-status-warning/15 px-1.5 text-xs font-medium text-status-warning">
            {unreadReleaseCount}
          </span>
        )}
      </Link>

      <Link
        href="/settings/learning"
        role="menuitem"
        className={itemClass}
        onClick={onClose}
      >
        <span className="font-medium text-fg">Learning preferences</span>
      </Link>

      <div className="my-1 border-t border-border" />

      <label className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-2 text-sm hover:bg-canvas">
        <input
          type="checkbox"
          checked={emailDigestOn}
          onChange={(e) => updatePreferences({ emailDigestEnabled: e.target.checked })}
          className="rounded border-border"
        />
        <span className="text-fg">Email me What&apos;s New (auto once per day when unread)</span>
      </label>

      {emailDigestOn && unreadReleaseCount > 0 && (
        <button
          type="button"
          role="menuitem"
          className={itemClass}
          disabled={digestMut.isPending}
          onClick={() => digestMut.mutate()}
        >
          <Mail className="h-4 w-4 shrink-0" />
          {digestMut.isPending ? "Sending…" : `Email ${unreadReleaseCount} update(s)`}
        </button>
      )}
      {digestMsg && <p className="px-2 text-xs text-fg-muted">{digestMsg}</p>}

      <div className="my-1 border-t border-border" />

      <p className="px-2 py-2 text-[10px] font-semibold uppercase tracking-widest text-fg-muted">
        Quick actions
      </p>

      <button
        type="button"
        role="menuitem"
        className={itemClass}
        onClick={() => {
          setMenuOpen(false);
          setAiPanelOpen(true);
          onClose();
        }}
      >
        <Bot className="h-4 w-4 shrink-0 text-brand-600 dark:text-brand-100" />
        <span className="font-medium text-fg">Ask learning assistant</span>
      </button>

      <button
        type="button"
        role="menuitem"
        className={itemClass}
        onClick={() => {
          getTourShellActions().openCommandPalette?.();
          onClose();
        }}
      >
        <Search className="h-4 w-4 shrink-0" />
        <span className="font-medium text-fg">Search features</span>
        <kbd className="ml-auto rounded-md border border-border bg-canvas px-1.5 py-0.5 font-mono text-[10px] text-fg-muted">
          Ctrl K
        </kbd>
      </button>

      <button
        type="button"
        role="menuitem"
        className={itemClass}
        onClick={() => {
          getTourShellActions().openShortcutsHelp?.();
          onClose();
        }}
      >
        <Keyboard className="h-4 w-4 shrink-0" />
        <span className="font-medium text-fg">Keyboard shortcuts</span>
      </button>

      <div className="sticky bottom-0 mt-2 flex justify-end border-t border-border/60 bg-surface/90 px-2 py-2 backdrop-blur-sm">
        <Button type="button" variant="ghost" size="sm" onClick={onClose}>
          Close
        </Button>
      </div>
    </LearningHubPanel>
  );
}
