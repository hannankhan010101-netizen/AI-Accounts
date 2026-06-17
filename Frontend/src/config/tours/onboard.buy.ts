import type { TourDefinition } from "@/lib/tour/types";

export const onboardBuyTour: TourDefinition = {
  id: "onboard.buy",
  version: 1,
  type: "onboard",
  title: "Buy — supplier bills",
  module: "purchases",
  personas: ["general", "procurement", "accountant", "admin"],
  prerequisites: { completedTours: ["onboard.core"] },
  metadata: { estimatedMinutes: 4, priority: 70 },
  steps: [
    {
      id: "bills-list",
      target: { kind: "tour", id: "purchase-bills-header" },
      presentation: "spotlight",
      content: {
        title: "Supplier bills",
        why: "Bills record what you owe suppliers and feed AP aging.",
        how: "Use this list to track draft, approved, and paid bills.",
      },
      placement: "bottom",
    },
    {
      id: "new-bill",
      target: { kind: "tour", id: "purchase-bills-new" },
      presentation: "spotlight",
      content: {
        title: "Record a bill",
        how: "Create a bill with supplier, dates, and line items before payment.",
      },
      placement: "left",
    },
    {
      id: "suppliers",
      target: { kind: "tour", id: "sidebar-nav" },
      presentation: "panel",
      content: {
        title: "Suppliers",
        how: "Maintain supplier master data under **Buy → Suppliers**.",
      },
    },
  ],
};
