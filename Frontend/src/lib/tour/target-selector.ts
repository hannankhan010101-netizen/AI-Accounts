import type { TourTargetSpec } from "@/lib/tour/types";

export function tourTargetSelector(spec: TourTargetSpec): string | null {
  if (spec.kind === "panel") return null;
  if (spec.kind === "grid") {
    if (spec.rowIndex !== undefined) {
      return `[data-tour="${spec.id}-row-${spec.rowIndex}"]`;
    }
    return `[data-tour="${spec.id}"]`;
  }
  return `[data-tour="${spec.id}"]`;
}
