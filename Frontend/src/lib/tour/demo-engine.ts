/** @deprecated Import from `@/lib/tour/workflow-engine` — re-exports for compatibility. */
export {
  executeTourAction,
  resolveEnterAction,
  shouldAutoAdvance,
  shouldAutoContinue,
  waitForRoute,
  waitForValidation,
  validateStep,
} from "@/lib/tour/workflow-engine";

import type { TourDefinition, TourStep } from "@/lib/tour/types";
import { isInteractiveTour, resolveTourExperience } from "@/lib/tour/types";

export function shouldShowDemoCursor(def: TourDefinition, step: TourStep): boolean {
  if (step.cursor?.enabled === false) return false;
  if (step.cursor?.enabled === true) return true;
  return isInteractiveTour(def) && step.target.kind === "tour";
}

export function getExperienceLabel(def: TourDefinition): string {
  const mode = resolveTourExperience(def);
  if (mode === "practice") return "Practice mode";
  if (mode === "interactive") return "Interactive demo";
  return "Guided tour";
}
