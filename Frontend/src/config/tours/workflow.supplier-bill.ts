import type { TourDefinition } from "@/lib/tour/types";

/** Guided create supplier bill flow — list → new form → save. */
export const workflowSupplierBillTour: TourDefinition = {
  id: "workflow.supplier-bill",
  version: 1,
  type: "workflow",
  title: "Create a supplier bill",
  module: "purchases",
  personas: ["general", "procurement", "admin", "accountant"],
  prerequisites: {
    completedTours: ["onboard.core"],
    permissions: ["purchases.bills.create"],
  },
  metadata: { estimatedMinutes: 5, priority: 71 },
  steps: [
    {
      id: "open-new",
      target: { kind: "tour", id: "purchase-bills-new" },
      presentation: "spotlight",
      content: {
        title: "Start a new bill",
        why: "Supplier bills record AP and inventory costs.",
        how: "Click **Next** to open the bill form — the tour continues there.",
      },
      placement: "left",
      action: { type: "navigate", href: "/purchases/bills/new" },
    },
    {
      id: "header",
      target: { kind: "tour", id: "bill-new-header" },
      presentation: "spotlight",
      content: {
        title: "Header fields",
        how: "Select the **supplier** and **bill date** before adding lines.",
      },
      placement: "bottom",
    },
    {
      id: "lines",
      target: { kind: "tour", id: "bill-new-lines" },
      presentation: "spotlight",
      content: {
        title: "Line items",
        how: "Enter quantities, rates, and tax per line. Add rows with **Add line**.",
      },
      placement: "top",
    },
    {
      id: "summary",
      target: { kind: "tour", id: "bill-new-summary" },
      presentation: "spotlight",
      content: {
        title: "Live summary",
        how: "Check totals in the summary panel before saving.",
      },
      placement: "left",
    },
    {
      id: "save",
      target: { kind: "tour", id: "bill-new-save" },
      presentation: "spotlight",
      content: {
        title: "Save when ready",
        how: "Click **Save bill** to create the document.",
      },
      placement: "bottom",
      skippable: false,
    },
  ],
};
