import type { TourDefinition } from "@/lib/tour/types";

export const releaseInvoiceVoidTour: TourDefinition = {
  id: "release.invoice-void",
  version: 1,
  type: "release",
  title: "Void & replace invoices",
  module: "sales",
  personas: ["general", "sales", "accountant", "admin"],
  metadata: { estimatedMinutes: 2, priority: 50 },
  steps: [
    {
      id: "intro",
      target: { kind: "panel" },
      presentation: "panel",
      content: {
        title: "What's new",
        why: "Correct mistakes without losing audit history.",
        how: "Void a posted invoice, then create a replacement draft from the detail screen.",
      },
      skippable: true,
    },
    {
      id: "invoices",
      target: { kind: "tour", id: "sales-invoices-header" },
      presentation: "spotlight",
      content: {
        title: "Start from invoices",
        how: "Open an invoice, use **Void**, then **Create replacement** when you need a corrected copy.",
      },
      placement: "bottom",
    },
  ],
};
