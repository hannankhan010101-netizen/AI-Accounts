import type { TourDefinition } from "@/lib/tour/types";

export const releaseBankReconTour: TourDefinition = {
  id: "release.bank-recon",
  version: 1,
  type: "release",
  title: "Complete reconciliation",
  module: "bank",
  personas: ["general", "accountant", "cfo", "admin"],
  metadata: { estimatedMinutes: 2, priority: 45 },
  steps: [
    {
      id: "intro",
      target: { kind: "panel" },
      presentation: "panel",
      content: {
        title: "What's new",
        how: "When every statement line is matched, use **Complete reconciliation** to close the period.",
      },
      skippable: true,
    },
    {
      id: "list",
      target: { kind: "tour", id: "bank-reconciliation-header" },
      presentation: "spotlight",
      content: {
        title: "Reconciliation workspace",
        how: "Open a reconciliation, match items, then complete when balances agree.",
      },
      placement: "bottom",
    },
  ],
};
