"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useReducer,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { usePathname, useRouter } from "next/navigation";

import { useCompany } from "@/lib/auth/company-context";
import { getTokens } from "@/lib/auth/storage";
import { getUserKeyFromAccessToken } from "@/lib/auth/jwt";
import { MOBILE_MEDIA_QUERY } from "@/lib/responsive/constants";
import { flushTourAnalyticsToServer, trackTourEvent } from "@/lib/tour/analytics";
import { filterTourForContext } from "@/lib/tour/filters";
import { resolvePersona } from "@/lib/tour/persona";
import {
  computeMaturityScore,
  getTourEntry,
  readActiveSession,
  updateTourEntry,
  writeActiveSession,
} from "@/lib/tour/progress-store";
import { useTourSync } from "@/lib/tour/use-tour-sync";
import { getTourDefinition, preloadTour } from "@/lib/tour/registry";
import { prefetchTourRoute } from "@/lib/tour/route-prefetch";
import { computeFeatureHints } from "@/lib/tour/feature-hints";
import { rankFeatureHints } from "@/lib/tour/hint-ranker";
import { maybeSendAutoDigest } from "@/lib/tour/digest-scheduler";
import { countUnreadReleases, releaseDismissKey } from "@/lib/tour/release-feed";
import { toursForPath } from "@/lib/tour/route-tours";
import { getTourShellActions } from "@/lib/tour/shell-actions";
import { tourTargetSelector } from "@/lib/tour/target-selector";
import {
  isOversizedTourTarget,
  measureTarget,
  resolveTourMeasureElement,
  scrollTargetIntoView,
  waitForTourTarget,
  type TargetRect,
} from "@/lib/tour/target-resolver";
import {
  executeTourAction,
  resolveInitialStepIndex,
  runStepWorkflow,
  shouldAutoAdvance,
  shouldAutoContinue,
  waitForValidation,
} from "@/lib/tour/workflow-engine";
import type {
  FeatureHint,
  ReleaseItem,
  ResumeOffer,
  TourDefinition,
  TourExperienceMode,
  TourMachineState,
  TourPreferences,
  TourStep,
  UserTourProgress,
} from "@/lib/tour/types";
import { resolveTourExperience } from "@/lib/tour/types";
import { useTourUIStore } from "@/stores/onboarding/tour-ui-store";

type RunningTour = {
  definition: TourDefinition;
  steps: TourStep[];
  stepIndex: number;
};

type TourState = {
  machine: TourMachineState;
  running: RunningTour | null;
  targetRect: TargetRect | null;
  panelOnly: boolean;
  menuOpen: boolean;
  attentionPulse: boolean;
  progress: UserTourProgress;
};

type Action =
  | { type: "SET_PROGRESS"; progress: UserTourProgress }
  | { type: "SET_MENU"; open: boolean }
  | { type: "SET_ATTENTION"; on: boolean }
  | { type: "START"; running: RunningTour }
  | { type: "SET_TARGET"; rect: TargetRect | null; panelOnly: boolean }
  | { type: "ADVANCE" }
  | { type: "PAUSE" }
  | { type: "DISMISS" }
  | { type: "COMPLETE" };

function reducer(state: TourState, action: Action): TourState {
  switch (action.type) {
    case "SET_PROGRESS":
      return { ...state, progress: action.progress };
    case "SET_MENU":
      return { ...state, menuOpen: action.open };
    case "SET_ATTENTION":
      return { ...state, attentionPulse: action.on };
    case "START":
      return {
        ...state,
        machine: "running",
        running: action.running,
        menuOpen: false,
        panelOnly: false,
      };
    case "SET_TARGET":
      return {
        ...state,
        targetRect: action.rect,
        panelOnly: action.panelOnly,
        machine:
          state.running && (state.machine === "waiting_target" || state.machine === "paused")
            ? "running"
            : state.running
              ? "running"
              : state.machine,
      };
    case "ADVANCE": {
      if (!state.running) return state;
      const nextIndex = state.running.stepIndex + 1;
      if (nextIndex >= state.running.steps.length) {
        return { ...state, machine: "completed", running: null, targetRect: null };
      }
      return {
        ...state,
        running: { ...state.running, stepIndex: nextIndex },
        targetRect: null,
        panelOnly: false,
        machine: "waiting_target",
      };
    }
    case "PAUSE":
      return { ...state, machine: "paused" };
    case "DISMISS":
      return {
        ...state,
        machine: "idle",
        running: null,
        targetRect: null,
        panelOnly: false,
      };
    case "COMPLETE":
      return {
        ...state,
        machine: "idle",
        running: null,
        targetRect: null,
        panelOnly: false,
      };
    default:
      return state;
  }
}

type TourContextValue = {
  machine: TourMachineState;
  menuOpen: boolean;
  setMenuOpen: (open: boolean) => void;
  attentionPulse: boolean;
  progress: UserTourProgress;
  running: RunningTour | null;
  currentStep: TourStep | null;
  targetRect: TargetRect | null;
  panelOnly: boolean;
  persona: ReturnType<typeof resolvePersona>;
  permissions: string[];
  roleName: string | null;
  startTour: (tourId: string, fromStep?: number) => void;
  nextStep: () => void;
  skipStep: () => void;
  skipTour: () => void;
  dismissTour: () => void;
  continueTour: () => void;
  suggestedTourId: string;
  pageTourIds: string[];
  resumeOffer: ResumeOffer | null;
  dismissResumeOffer: () => void;
  resumeFromOffer: () => void;
  featureHints: FeatureHint[];
  dismissFeatureHint: (hintId: string) => void;
  releases: ReleaseItem[];
  unreadReleaseCount: number;
  dismissRelease: (releaseId: string) => void;
  aiPanelOpen: boolean;
  setAiPanelOpen: (open: boolean) => void;
  updatePreferences: (patch: Partial<TourPreferences>) => void;
  completionToast: string | null;
  completionMessage: string | null;
  clearCompletionToast: () => void;
  experienceMode: TourExperienceMode;
  practiceMode: boolean;
  /** Interactive demo on a form — block real saves, allow ghost fill. */
  isDemoSandbox: boolean;
};

const TourContext = createContext<TourContextValue | null>(null);

function userKeyFromToken(): string {
  const tokens = getTokens();
  if (!tokens) return "anonymous";
  return getUserKeyFromAccessToken(tokens.accessToken);
}

export function TourProvider({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { companyId } = useCompany();
  const userKey = useMemo(() => userKeyFromToken(), []);
  const { loadMerged, schedulePut } = useTourSync(companyId, userKey);
  const [permissions, setPermissions] = useState<string[]>([]);
  const [roleName, setRoleName] = useState<string | null>(null);
  const [resumeOffer, setResumeOffer] = useState<ResumeOffer | null>(null);
  const [resumeDismissed, setResumeDismissed] = useState(false);
  const [releases, setReleases] = useState<ReleaseItem[]>([]);
  const [aiPanelOpen, setAiPanelOpen] = useState(false);
  const [completionToast, setCompletionToast] = useState<string | null>(null);
  const [completionMessage, setCompletionMessage] = useState<string | null>(null);
  const practiceMode = useTourUIStore((s) => s.practiceMode);
  const clearCompletionToast = useCallback(() => {
    setCompletionToast(null);
    setCompletionMessage(null);
  }, []);
  const persona = useMemo(
    () => resolvePersona(permissions, roleName),
    [permissions, roleName],
  );

  const [state, dispatch] = useReducer(reducer, {
    machine: "idle",
    running: null,
    targetRect: null,
    panelOnly: false,
    menuOpen: false,
    attentionPulse: false,
    progress: { tours: {}, maturityScore: 0, dismissedHints: [] },
  });

  const stateRef = useRef(state);
  stateRef.current = state;

  const persist = useCallback(
    (progress: UserTourProgress) => {
      if (!companyId) return;
      const scored = { ...progress, maturityScore: computeMaturityScore(progress) };
      dispatch({ type: "SET_PROGRESS", progress: scored });
      schedulePut(scored);
    },
    [companyId, schedulePut],
  );

  useEffect(() => {
    if (!companyId) return;
    let cancelled = false;
    void loadMerged().then((data) => {
      if (cancelled || !data) return;
      dispatch({ type: "SET_PROGRESS", progress: data.progress });
      setPermissions(data.permissions);
      setRoleName(data.roleName);
      setReleases(data.releases);
      const entry = data.progress.tours["onboard.core"];
      const unread = countUnreadReleases(data.releases, data.progress);
      const pulse =
        unread > 0 || !entry || entry.status === "not_started";
      dispatch({ type: "SET_ATTENTION", on: pulse });
      void maybeSendAutoDigest(companyId, userKey, data.progress, data.releases);
    });
    return () => {
      cancelled = true;
    };
  }, [companyId, loadMerged, userKey]);

  useEffect(() => {
    function onHide() {
      if (document.visibilityState === "hidden") void flushTourAnalyticsToServer();
    }
    document.addEventListener("visibilitychange", onHide);
    return () => document.removeEventListener("visibilitychange", onHide);
  }, []);

  const applyTargetFromElement = useCallback(
    (step: TourStep, el: HTMLElement | null) => {
      if (!el) {
        trackTourEvent({
          event: "target_missing",
          tourId: stateRef.current.running?.definition.id ?? "",
          stepId: step.id,
          pathname,
          companyId,
        });
        dispatch({ type: "SET_TARGET", rect: null, panelOnly: true });
        return;
      }
      const targetId = step.target.kind === "tour" ? step.target.id : undefined;
      const measureEl = resolveTourMeasureElement(el, targetId);

      const applyRect = () => {
        const rect = measureTarget(measureEl);
        if (!rect) {
          dispatch({ type: "SET_TARGET", rect: null, panelOnly: true });
          return;
        }
        const panelOnly = isOversizedTourTarget(rect, targetId);
        dispatch({
          type: "SET_TARGET",
          rect: panelOnly ? null : rect,
          panelOnly,
        });
      };

      applyRect();
      requestAnimationFrame(() => {
        requestAnimationFrame(applyRect);
      });
    },
    [companyId, pathname],
  );

  const resolveStepTarget = useCallback(
    (step: TourStep) => {
      const running = stateRef.current.running;
      if (!running) return () => {};

      if (step.target.kind === "panel") {
        dispatch({ type: "SET_TARGET", rect: null, panelOnly: true });
        return () => {};
      }

      dispatch({ type: "SET_TARGET", rect: null, panelOnly: false });
      let cancelled = false;

      void runStepWorkflow({
        def: running.definition,
        step,
        push: (href) => router.push(href),
        onNavigating: (on) => useTourUIStore.getState().setWorkflowNavigating(on),
        onTargetReady: () => {
          if (cancelled) return;
          waitForTourTarget(step.target, (el) => {
            if (!cancelled) applyTargetFromElement(step, el);
          });
        },
      });

      return () => {
        cancelled = true;
        useTourUIStore.getState().setWorkflowNavigating(false);
      };
    },
    [applyTargetFromElement, companyId, pathname, router],
  );

  useEffect(() => {
    const running = state.running;
    if (!running || state.machine === "idle" || state.machine === "completed") return;
    const step = running.steps[running.stepIndex];
    if (!step) return;

    const shell = getTourShellActions();
    const isMobile =
      typeof window !== "undefined" && window.matchMedia(MOBILE_MEDIA_QUERY).matches;

    if (step.id === "navigation") {
      if (isMobile) shell.openMobileNav?.();
      else {
        shell.closeMobileNav?.();
        shell.ensureSidebarExpanded?.();
      }
    } else {
      shell.closeMobileNav?.();
    }
    if (step.id === "company" || step.id === "search" || step.id === "help") {
      shell.closeCommandPalette?.();
      shell.closeCompanyMenu?.();
    }
    if (step.id === "help") {
      dispatch({ type: "SET_MENU", open: false });
    }

    trackTourEvent({
      event: "step_viewed",
      tourId: running.definition.id,
      stepId: step.id,
      stepIndex: running.stepIndex,
      pathname,
      companyId,
    });

    let cancelTarget = () => {};
    const delayMs = step.id === "navigation" && isMobile ? 280 : 120;

    const timer = window.setTimeout(() => {
      cancelTarget = resolveStepTarget(step);
    }, delayMs);

    return () => {
      window.clearTimeout(timer);
      cancelTarget();
    };
  }, [
    state.running?.stepIndex,
    state.running?.definition.id,
    resolveStepTarget,
    state.machine,
    pathname,
    companyId,
  ]);

  useEffect(() => {
    const step = state.running?.steps[state.running.stepIndex];
    if (!step || step.target.kind === "panel" || state.panelOnly) return;
    const sel = tourTargetSelector(step.target);
    if (!sel) return;
    const target = document.querySelector<HTMLElement>(sel);
    if (!target) return;
    const targetId = step.target.kind === "tour" ? step.target.id : undefined;
    const measureEl = resolveTourMeasureElement(target, targetId);
    const ro = new ResizeObserver(() => {
      dispatch({
        type: "SET_TARGET",
        rect: measureTarget(measureEl),
        panelOnly: false,
      });
    });
    ro.observe(measureEl);
    window.addEventListener("scroll", onScroll, true);
    window.addEventListener("resize", onScroll);
    function onScroll() {
      dispatch({
        type: "SET_TARGET",
        rect: measureTarget(measureEl),
        panelOnly: false,
      });
    }
    return () => {
      ro.disconnect();
      window.removeEventListener("scroll", onScroll, true);
      window.removeEventListener("resize", onScroll);
    };
  }, [state.running, state.targetRect, state.panelOnly]);

  const runTour = useCallback(
    (def: TourDefinition, tourId: string, fromStep: number) => {
      if (!companyId) return;
      const filtered = filterTourForContext(def, {
        persona,
        permissions,
        progress: stateRef.current.progress,
      });
      if (!filtered || filtered.steps.length === 0) return;

      const steps = filtered.steps;
      const effectiveDef: TourDefinition =
        practiceMode && resolveTourExperience(filtered) !== "practice"
          ? { ...filtered, experience: "practice" }
          : filtered;
      let stepIndex = resolveInitialStepIndex(effectiveDef, steps, fromStep, pathname);
      const firstNav = steps[stepIndex];
      const prefetchHref =
        firstNav?.enterAction?.type === "navigate" ||
        firstNav?.enterAction?.type === "sidebarNavigate"
          ? firstNav.enterAction.href
          : firstNav?.action?.type === "navigate"
            ? firstNav.action.href
            : null;
      if (prefetchHref) prefetchTourRoute(prefetchHref);

      const entry = getTourEntry(stateRef.current.progress, tourId, effectiveDef.version);
      const isReplay = entry.status === "completed";

      dispatch({ type: "SET_MENU", open: false });
      dispatch({
        type: "START",
        running: { definition: effectiveDef, steps, stepIndex },
      });
      writeActiveSession({
        tourId,
        stepIndex,
        startedAt: Date.now(),
      });

      persist(
        updateTourEntry(stateRef.current.progress, tourId, {
          ...entry,
          status: "in_progress",
          stepIndex,
          version: effectiveDef.version,
        }),
      );

      trackTourEvent({
        event: isReplay ? "tour_replayed" : "tour_started",
        tourId,
        stepIndex,
        pathname,
        companyId,
      });
      dispatch({ type: "SET_ATTENTION", on: false });
      setResumeOffer(null);
      setResumeDismissed(false);
    },
    [companyId, persona, permissions, pathname, persist, practiceMode],
  );

  const startTour = useCallback(
    (tourId: string, fromStep = 0) => {
      const eager = getTourDefinition(tourId);
      if (eager) {
        runTour(eager, tourId, fromStep);
        return;
      }
      void preloadTour(tourId).then((def) => {
        if (def) runTour(def, tourId, fromStep);
      });
    },
    [runTour],
  );

  const finishTour = useCallback(
    (status: "completed" | "skipped") => {
      const running = stateRef.current.running;
      if (!running || !companyId) {
        dispatch({ type: "DISMISS" });
        writeActiveSession(null);
        return;
      }
      const { id, version } = running.definition;
      const now = new Date().toISOString();
      persist(
        updateTourEntry(stateRef.current.progress, id, {
          status,
          stepIndex: running.stepIndex,
          version,
          ...(status === "completed" ? { completedAt: now } : { skippedAt: now }),
        }),
      );
      trackTourEvent({
        event: status === "completed" ? "tour_completed" : "tour_dismissed",
        tourId: id,
        pathname,
        companyId,
      });
      void flushTourAnalyticsToServer();
      if (status === "completed") {
        setCompletionToast(running.definition.title);
        setCompletionMessage(
          running.definition.metadata.celebrationMessage ??
            "Your progress is saved. Run this demo again anytime from Learn.",
        );
      }
      dispatch({ type: status === "completed" ? "COMPLETE" : "DISMISS" });
      writeActiveSession(null);
    },
    [companyId, pathname, persist],
  );

  const nextStep = useCallback(() => {
    const running = stateRef.current.running;
    if (!running) return;
    const step = running.steps[running.stepIndex];
    trackTourEvent({
      event: "step_completed",
      tourId: running.definition.id,
      stepId: step?.id,
      stepIndex: running.stepIndex,
      pathname,
      companyId,
    });
    if (running.stepIndex >= running.steps.length - 1) {
      finishTour("completed");
      return;
    }
    const nextIndex = running.stepIndex + 1;
    if (companyId) {
      persist(
        updateTourEntry(stateRef.current.progress, running.definition.id, {
          ...getTourEntry(
            stateRef.current.progress,
            running.definition.id,
            running.definition.version,
          ),
          status: "in_progress",
          stepIndex: nextIndex,
          version: running.definition.version,
        }),
      );
      writeActiveSession({
        tourId: running.definition.id,
        stepIndex: nextIndex,
        startedAt: Date.now(),
      });
    }
    if (step?.action) {
      if (step.action.type === "navigate") {
        prefetchTourRoute(step.action.href);
      }
      void executeTourAction(step.action, router.push);
    }
    const upcoming = running.steps[nextIndex];
    if (upcoming?.action?.type === "navigate") {
      prefetchTourRoute(upcoming.action.href);
    }
    dispatch({ type: "ADVANCE" });
  }, [companyId, finishTour, pathname, persist, router]);

  const nextStepRef = useRef(nextStep);
  nextStepRef.current = nextStep;
  const autoContinuedKeyRef = useRef<string | null>(null);

  useEffect(() => {
    const running = state.running;
    if (
      !running ||
      (state.machine !== "running" && state.machine !== "waiting_target")
    ) {
      return;
    }
    const step = running.steps[running.stepIndex];
    if (!step || !shouldAutoContinue(running.definition, step)) return;
    if (shouldAutoAdvance(running.definition, step)) return;

    const stepKey = `${running.definition.id}:${running.stepIndex}`;
    if (autoContinuedKeyRef.current === stepKey) return;

    const ready =
      step.target.kind === "panel" ||
      state.panelOnly ||
      Boolean(state.targetRect);
    if (!ready) return;

    autoContinuedKeyRef.current = stepKey;
    const delayMs = step.autoContinueDelayMs ?? 1000;

    const timer = window.setTimeout(() => {
      void waitForValidation(step, window.location.pathname, 8000).then(async (ok) => {
        if (stateRef.current.running?.stepIndex !== running.stepIndex) return;
        if (!ok && step.enterAction) {
          await executeTourAction(step.enterAction, (href) => router.push(href));
          ok = await waitForValidation(step, window.location.pathname, 6000);
        }
        if (ok) nextStepRef.current();
      });
    }, delayMs);

    return () => window.clearTimeout(timer);
  }, [
    state.running?.stepIndex,
    state.running?.definition.id,
    state.machine,
    state.targetRect,
    state.panelOnly,
    pathname,
    router,
  ]);

  useEffect(() => {
    autoContinuedKeyRef.current = null;
  }, [state.running?.stepIndex, state.running?.definition.id]);

  const skipStep = useCallback(() => {
    trackTourEvent({
      event: "step_skipped",
      tourId: stateRef.current.running?.definition.id ?? "",
      stepIndex: stateRef.current.running?.stepIndex,
      pathname,
      companyId,
    });
    nextStep();
  }, [companyId, nextStep, pathname]);

  useEffect(() => {
    const running = state.running;
    if (
      !running ||
      (state.machine !== "running" && state.machine !== "waiting_target")
    ) {
      return;
    }
    const step = running.steps[running.stepIndex];
    if (!step || !shouldAutoAdvance(running.definition, step)) return;

    let cancelled = false;
    let timer: number | undefined;
    void waitForValidation(step, pathname, 10000).then((ok) => {
      if (cancelled || !ok || !step.autoAdvanceMs) return;
      timer = window.setTimeout(() => {
        if (!cancelled) nextStep();
      }, step.autoAdvanceMs);
    });

    return () => {
      cancelled = true;
      if (timer) window.clearTimeout(timer);
    };
  }, [
    state.running?.stepIndex,
    state.running?.definition.id,
    state.machine,
    pathname,
    nextStep,
    state.running,
  ]);

  const skipTour = useCallback(() => finishTour("skipped"), [finishTour]);

  const dismissTour = useCallback(() => {
    trackTourEvent({
      event: "tour_dismissed",
      tourId: stateRef.current.running?.definition.id ?? "",
      pathname,
      companyId,
    });
    if (stateRef.current.running && companyId) {
      const r = stateRef.current.running;
      persist(
        updateTourEntry(stateRef.current.progress, r.definition.id, {
          ...getTourEntry(stateRef.current.progress, r.definition.id, r.definition.version),
          status: "in_progress",
          stepIndex: r.stepIndex,
          version: r.definition.version,
        }),
      );
    }
    dispatch({ type: "DISMISS" });
    writeActiveSession(null);
  }, [companyId, pathname, persist]);

  const continueTour = useCallback(() => {
    const session = readActiveSession();
    if (session) {
      startTour(session.tourId, session.stepIndex);
      return;
    }
    const inProgress = Object.entries(stateRef.current.progress.tours).find(
      ([, e]) => e.status === "in_progress",
    );
    if (inProgress) {
      const [tourId, entry] = inProgress;
      startTour(tourId, entry.stepIndex ?? 0);
      return;
    }
    startTour("onboard.core");
  }, [startTour]);

  useEffect(() => {
    if (resumeDismissed || state.machine !== "idle" || state.running) {
      if (state.running) setResumeOffer(null);
      return;
    }

    const session = readActiveSession();
    const inProgressEntry = Object.entries(state.progress.tours).find(
      ([, e]) => e.status === "in_progress",
    );

    const tourId = session?.tourId ?? inProgressEntry?.[0];
    if (!tourId) {
      setResumeOffer(null);
      return;
    }

    const def = getTourDefinition(tourId);
    if (!def) {
      setResumeOffer(null);
      return;
    }

    const entry = state.progress.tours[tourId];
    if (entry?.status !== "in_progress" && entry?.status !== undefined) {
      setResumeOffer(null);
      return;
    }

    const stepIndex = session?.stepIndex ?? entry?.stepIndex ?? 0;
    setResumeOffer({
      tourId,
      stepIndex,
      title: def.title,
      stepCount: def.steps.length,
    });
  }, [
    resumeDismissed,
    state.machine,
    state.running,
    state.progress.tours,
  ]);

  const autoResumedRef = useRef(false);
  useEffect(() => {
    if (!companyId || autoResumedRef.current || resumeDismissed) return;
    if (state.machine !== "idle" || state.running) return;

    const session = readActiveSession();
    if (!session) return;

    const entry = state.progress.tours[session.tourId];
    if (entry?.status === "completed") {
      writeActiveSession(null);
      return;
    }

    autoResumedRef.current = true;
    const t = window.setTimeout(() => {
      startTour(session.tourId, session.stepIndex);
    }, 400);
    return () => window.clearTimeout(t);
  }, [companyId, resumeDismissed, startTour, state.machine, state.running, state.progress.tours]);

  const dismissResumeOffer = useCallback(() => {
    setResumeDismissed(true);
    setResumeOffer(null);
    writeActiveSession(null);
  }, []);

  const resumeFromOffer = useCallback(() => {
    if (!resumeOffer) return;
    setResumeDismissed(true);
    setResumeOffer(null);
    startTour(resumeOffer.tourId, resumeOffer.stepIndex);
  }, [resumeOffer, startTour]);

  const dismissFeatureHint = useCallback(
    (hintId: string) => {
      if (stateRef.current.progress.dismissedHints.includes(hintId)) return;
      persist({
        ...stateRef.current.progress,
        dismissedHints: [...stateRef.current.progress.dismissedHints, hintId],
      });
    },
    [persist],
  );

  const dismissRelease = useCallback(
    (releaseId: string) => {
      const key = releaseDismissKey(releaseId);
      if (stateRef.current.progress.dismissedHints.includes(key)) return;
      persist({
        ...stateRef.current.progress,
        dismissedHints: [...stateRef.current.progress.dismissedHints, key],
      });
    },
    [persist],
  );

  const updatePreferences = useCallback(
    (patch: Partial<TourPreferences>) => {
      const prev = stateRef.current.progress.preferences ?? {
        emailDigestEnabled: false,
      };
      persist({
        ...stateRef.current.progress,
        preferences: { ...prev, ...patch },
      });
    },
    [persist],
  );

  const unreadReleaseCount = useMemo(
    () => countUnreadReleases(releases, state.progress),
    [releases, state.progress],
  );

  const featureHints = useMemo(() => {
    const raw = computeFeatureHints({
      progress: state.progress,
      permissions,
      persona,
    });
    return rankFeatureHints(raw, {
      pathname,
      persona,
      progress: state.progress,
    });
  }, [state.progress, permissions, persona, pathname]);

  const pageTourIds = useMemo(() => toursForPath(pathname), [pathname]);
  const suggestedTourId: string = pageTourIds[0] ?? "onboard.core";

  const currentStep =
    state.running && state.running.steps[state.running.stepIndex]
      ? state.running.steps[state.running.stepIndex]
      : null;

  const experienceMode: TourExperienceMode = state.running
    ? resolveTourExperience(state.running.definition)
    : "guided";

  const isDemoSandbox = Boolean(
    state.running &&
      (state.machine === "running" || state.machine === "waiting_target") &&
      (state.running.definition.type === "demo" || practiceMode),
  );

  const value = useMemo<TourContextValue>(
    () => ({
      machine: state.machine,
      menuOpen: state.menuOpen,
      setMenuOpen: (open) => dispatch({ type: "SET_MENU", open }),
      attentionPulse: state.attentionPulse,
      progress: state.progress,
      running: state.running,
      currentStep,
      targetRect: state.targetRect,
      panelOnly: state.panelOnly,
      persona,
      permissions,
      roleName,
      startTour,
      nextStep,
      skipStep,
      skipTour,
      dismissTour,
      continueTour,
      suggestedTourId,
      pageTourIds,
      resumeOffer,
      dismissResumeOffer,
      resumeFromOffer,
      featureHints,
      dismissFeatureHint,
      releases,
      unreadReleaseCount,
      dismissRelease,
      aiPanelOpen,
      setAiPanelOpen,
      updatePreferences,
      completionToast,
      completionMessage,
      clearCompletionToast,
      experienceMode,
      practiceMode,
      isDemoSandbox,
    }),
    [
      state,
      currentStep,
      persona,
      permissions,
      roleName,
      startTour,
      nextStep,
      skipStep,
      skipTour,
      dismissTour,
      continueTour,
      suggestedTourId,
      pageTourIds,
      resumeOffer,
      dismissResumeOffer,
      resumeFromOffer,
      featureHints,
      dismissFeatureHint,
      releases,
      unreadReleaseCount,
      dismissRelease,
      aiPanelOpen,
      setAiPanelOpen,
      updatePreferences,
      completionToast,
      completionMessage,
      experienceMode,
      practiceMode,
      isDemoSandbox,
    ],
  );

  return <TourContext.Provider value={value}>{children}</TourContext.Provider>;
}

export function useTour(): TourContextValue {
  const ctx = useContext(TourContext);
  if (!ctx) throw new Error("useTour must be used within TourProvider");
  return ctx;
}
