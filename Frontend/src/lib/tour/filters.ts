import { hasPermission } from "@/lib/rbac/permissions";
import type { PersonaId, TourDefinition, UserTourProgress } from "@/lib/tour/types";

export function filterTourForContext(
  tour: TourDefinition,
  ctx: {
    persona: PersonaId;
    permissions: string[];
    progress: UserTourProgress;
  },
): TourDefinition | null {
  if (
    tour.personas.length > 0 &&
    !tour.personas.includes("general") &&
    !tour.personas.includes(ctx.persona)
  ) {
    return null;
  }

  const required = tour.prerequisites?.permissions;
  if (
    required?.length &&
    !required.some((p) => hasPermission(ctx.permissions, p))
  ) {
    return null;
  }

  const completed = tour.prerequisites?.completedTours ?? [];
  if (
    completed.length &&
    !completed.every((id) => ctx.progress.tours[id]?.status === "completed")
  ) {
    return null;
  }

  return tour;
}
