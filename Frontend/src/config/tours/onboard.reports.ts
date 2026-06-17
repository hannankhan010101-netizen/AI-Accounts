import type { TourDefinition } from "@/lib/tour/types";

export const onboardReportsTour: TourDefinition = {
  id: "onboard.reports",
  version: 1,
  type: "module",
  title: "Insights — reports hub",
  module: "reports",
  personas: ["general", "accountant", "cfo", "admin", "viewer"],
  prerequisites: { completedTours: ["onboard.core"] },
  metadata: { estimatedMinutes: 3, priority: 70 },
  steps: [
    {
      id: "reports-header",
      target: { kind: "tour", id: "reports-hub-header" },
      presentation: "spotlight",
      content: {
        title: "Reports hub",
        why: "Financial and operational reports live in one searchable catalog.",
        how: "Star favorites for quick access from the dashboard and command palette.",
      },
      placement: "bottom",
    },
    {
      id: "search-reports",
      target: { kind: "tour", id: "reports-hub-search" },
      presentation: "spotlight",
      content: {
        title: "Find a report fast",
        how: "Search by name or category. Press **Ctrl+K** to jump to any report from anywhere.",
      },
      placement: "bottom",
    },
    {
      id: "favorites",
      target: { kind: "tour", id: "reports-hub-favorites" },
      presentation: "spotlight",
      content: {
        title: "Favorites",
        why: "Month-end teams revisit the same reports every period.",
        how: "Click the star on a report card to pin it to your favorites list.",
      },
      placement: "top",
      skippable: true,
    },
  ],
};
