/** Learner maturity labels from tour progress score. */

export type MaturityLevel = {
  id: string;
  label: string;
  minScore: number;
};

export const MATURITY_LEVELS: MaturityLevel[] = [
  { id: "starter", label: "Starter", minScore: 0 },
  { id: "explorer", label: "Explorer", minScore: 25 },
  { id: "regular", label: "Regular", minScore: 50 },
  { id: "pro", label: "Pro", minScore: 75 },
];

export function maturityLevelForScore(score: number): MaturityLevel {
  let current = MATURITY_LEVELS[0];
  for (const level of MATURITY_LEVELS) {
    if (score >= level.minScore) current = level;
  }
  return current;
}

export function completedTourCount(progress: {
  tours: Record<string, { status?: string }>;
}): number {
  return Object.values(progress.tours).filter((e) => e.status === "completed").length;
}
