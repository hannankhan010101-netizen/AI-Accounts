import type { FeatureHint, PersonaId, UserTourProgress } from "@/lib/tour/types";

/** Boost hints by route, persona, and learning gaps (P51). */
export function rankFeatureHints(
  hints: FeatureHint[],
  ctx: {
    pathname: string;
    persona: PersonaId;
    progress: UserTourProgress;
  },
): FeatureHint[] {
  const scored = hints.map((hint) => {
    let score = hint.priority;
    if (hint.href && ctx.pathname.startsWith(hint.href)) score += 25;
    if (hint.tourId) {
      const entry = ctx.progress.tours[hint.tourId];
      if (!entry || entry.status === "not_started") score += 15;
      if (entry?.status === "in_progress") score += 10;
    }
    if (hint.id === "hint.admin" && ctx.persona === "admin") score += 12;
    if (hint.id === "hint.sell" && ctx.persona === "sales") score += 12;
    if (ctx.progress.maturityScore < 30) score += 5;
    return { hint, score };
  });
  return scored
    .sort((a, b) => b.score - a.score)
    .map((s) => s.hint)
    .slice(0, 5);
}
