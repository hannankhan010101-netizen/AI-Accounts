/** Universal tour system — shared types (P0+ interactive). */



export type TourType =

  | "onboard"

  | "module"

  | "spotlight"

  | "workflow"

  | "task"

  | "release"

  | "ai"

  | "demo";



/** How the tour behaves for the learner. */

export type TourExperienceMode = "guided" | "interactive" | "practice";



export type TourPresentation = "spotlight" | "tooltip" | "panel" | "banner" | "none";



export type PersonaId =

  | "admin"

  | "accountant"

  | "sales"

  | "inventory_manager"

  | "procurement"

  | "cfo"

  | "viewer"

  | "general";



export type ModuleCode =

  | "sales"

  | "purchases"

  | "bank"

  | "inventory"

  | "assembly"

  | "financial"

  | "reports";



export type TourStepAction =

  | { type: "navigate"; href: string }

  | { type: "sidebarNavigate"; href: string; groupLabel?: string }

  | { type: "click"; tourTarget: string }

  | { type: "userConfirm" }

  | { type: "none" };



export type TourStepValidation =

  | { type: "elementVisible"; tourTarget: string; timeoutMs?: number }

  | { type: "routeMatch"; pathname: string }

  | { type: "none" };



export type TourTargetSpec =

  | { kind: "tour"; id: string }

  | { kind: "grid"; id: string; rowIndex?: number }

  | { kind: "panel" };



/** Sample data preview shown inside the step card during demos. */

export type TourDemoPreview = {

  id: string;

  headline: string;

  lines: string[];

  badge?: string;

};



/** Animated pointer toward the spotlight target. */

export type TourCursorConfig = {

  enabled?: boolean;

  /** Simulate a click pulse when the cursor reaches the target. */

  clickPulse?: boolean;

  /** Delay before the cursor starts moving (ms). */

  delayMs?: number;

};



export type FeatureHint = {

  id: string;

  title: string;

  body: string;

  ctaLabel: string;

  tourId?: string;

  href?: string;

  priority: number;

};



export type ResumeOffer = {

  tourId: string;

  stepIndex: number;

  title: string;

  stepCount: number;

};



export type ReleaseItem = {

  id: string;

  version: string;

  title: string;

  summary: string;

  publishedAt: string;

  tourId?: string | null;

  href?: string | null;

};



export type AiSuggestion = {

  id: string;

  title: string;

  reason: string;

  score: number;

  tourId?: string | null;

  href?: string | null;

};



export type OnboardingReleaseAdmin = {

  id: string;

  dbId: string;

  version: string;

  title: string;

  summary: string;

  publishedAt: string;

  tourId?: string | null;

  href?: string | null;

  permissions: string[];

  isActive: boolean;

  sortOrder: number;

  source?: string;

};



export type OnboardingInsights = {

  usersWithActivity: number;

  totalLearners: number;

  tourCompletion: Array<{

    tourId: string;

    started: number;

    completed: number;

    ratePercent: number;

  }>;

  topStepViews: Array<{ step: string; views: number }>;

};



export type MotionPresetId =

  | "fade"

  | "slideUp"

  | "scale"

  | "spotlight"

  | "tooltip"

  | "fab"

  | "drawer"

  | "navDrawer"

  | "bottomSheet";



export type TourStep = {

  id: string;

  target: TourTargetSpec;

  presentation: TourPresentation;

  content: {

    title: string;

    why?: string;

    how: string;

    bestPractice?: string;

    /** Conversational line from the AI guide persona. */

    assistantLine?: string;

  };

  placement?: "top" | "bottom" | "left" | "right" | "auto";

  /** Runs when the user advances (Next / Continue). */

  action?: TourStepAction;

  /** Runs when the step becomes active (auto-demo navigation). */

  enterAction?: TourStepAction;

  validation?: TourStepValidation;

  pauseAfterMs?: number;

  /** Auto-advance after validation + delay (interactive demos). */

  autoAdvanceMs?: number;

  /** After enterAction completes, advance to next step without clicking Next (demo default). */

  autoContinue?: boolean;

  /** Delay before auto-continue after step is ready (ms). */

  autoContinueDelayMs?: number;

  /** Run `enterAction` / navigate on step enter (default true for `demo` tours). */

  autoRunEnter?: boolean;

  skippable?: boolean;

  animation?: MotionPresetId;

  route?: string;

  demoPreviewId?: string;

  /** Recipe id in ghost-fill-recipes.ts — animates sample form values. */

  ghostFill?: string;

  cursor?: TourCursorConfig;

  /** Practice mode: user must click the spotlight target to continue. */

  requireTargetClick?: boolean;

  /** Custom prompt for the per-step AI coach. */

  assistantPrompt?: string;

};



export type TourDefinition = {

  id: string;

  version: number;

  type: TourType;

  title: string;

  module?: ModuleCode;

  personas: PersonaId[];

  prerequisites?: {

    permissions?: string[];

    completedTours?: string[];

  };

  steps: TourStep[];

  metadata: {

    estimatedMinutes: number;

    priority: number;

    celebrationMessage?: string;

    tagline?: string;

  };

  /** Defaults: `demo` → interactive, `workflow` → interactive, others → guided. */

  experience?: TourExperienceMode;

};



export type TourRunStatus = "not_started" | "in_progress" | "completed" | "skipped";



export type TourProgressEntry = {

  status: TourRunStatus;

  stepIndex: number;

  completedAt?: string;

  skippedAt?: string;

  version: number;

};



export type TourPreferences = {

  emailDigestEnabled: boolean;

  lastDigestSentAt?: string | null;

};



export type UserTourProgress = {

  tours: Record<string, TourProgressEntry>;

  maturityScore: number;

  dismissedHints: string[];

  lastActiveTourId?: string;

  preferences?: TourPreferences;

};



export type TourMachineState =

  | "idle"

  | "loading"

  | "running"

  | "waiting_target"

  | "paused"

  | "completed";



export type TourAnalyticsEventName =

  | "tour_started"

  | "tour_replayed"

  | "step_viewed"

  | "step_completed"

  | "step_skipped"

  | "tour_completed"

  | "tour_dismissed"

  | "target_missing"

  | "feature_adoption"

  | "demo_action"

  | "practice_click";



export function resolveTourExperience(def: TourDefinition): TourExperienceMode {

  if (def.experience) return def.experience;

  if (def.type === "demo" || def.type === "workflow") return "interactive";

  return "guided";

}



export function isInteractiveTour(def: TourDefinition): boolean {

  return resolveTourExperience(def) !== "guided";

}


