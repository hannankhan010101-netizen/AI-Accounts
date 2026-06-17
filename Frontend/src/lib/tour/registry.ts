import { onboardCoreTour } from "@/config/tours/onboard.core";
import {
  preloadTour as loadTourChunk,
  preloadToursForPath as prefetchPathTours,
  registerTourDefinition,
} from "@/lib/tour/lazy-registry";
import { toursForPath } from "@/lib/tour/route-tours";
import type { TourDefinition } from "@/lib/tour/types";

/** Always-available tours (welcome + critical path). */
const EAGER_TOURS: TourDefinition[] = [onboardCoreTour];

const registry = new Map<string, TourDefinition>(
  EAGER_TOURS.map((t) => [t.id, t]),
);
const tourList: TourDefinition[] = [...EAGER_TOURS];

export function preloadTour(tourId: string): Promise<TourDefinition | undefined> {
  return loadTourChunk(tourId, registry, tourList);
}

export function preloadToursForPath(pathname: string): void {
  prefetchPathTours(pathname, toursForPath(pathname), registry, tourList);
}

/** Warm common workflow chunks after idle. */
export function preloadCommonTours(): void {
  const common = [
    "onboard.sell",
    "onboard.money",
    "workflow.sales-invoice",
    "workflow.supplier-bill",
    "demo.sales-invoice",
    "demo.dashboard",
  ];
  for (const id of common) void preloadTour(id);
}

export function listWorkflowTours(): TourDefinition[] {
  return tourList.filter((t) => t.type === "workflow");
}

export function listDemoTours(): TourDefinition[] {
  return tourList
    .filter((t) => t.type === "demo")
    .sort((a, b) => b.metadata.priority - a.metadata.priority);
}

export function getTourDefinition(tourId: string): TourDefinition | undefined {
  return registry.get(tourId);
}

export function listTourDefinitions(): TourDefinition[] {
  return [...tourList];
}

export function listToursForPersona(persona: string): TourDefinition[] {
  return tourList
    .filter(
      (t) =>
        t.personas.includes("general") ||
        t.personas.includes(persona as TourDefinition["personas"][number]),
    )
    .sort((a, b) => b.metadata.priority - a.metadata.priority);
}

/** Register a tour at runtime (tests / CMS). */
export function registerTour(def: TourDefinition): void {
  registerTourDefinition(registry, tourList, def);
}
