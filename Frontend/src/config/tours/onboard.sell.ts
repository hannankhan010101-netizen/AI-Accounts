import type { TourDefinition } from "@/lib/tour/types";

export const onboardSellTour: TourDefinition = {
  id: "onboard.sell",
  version: 1,
  type: "onboard",
  title: "Sell — invoices & customers",
  module: "sales",
  personas: ["general", "sales", "admin", "accountant"],
  prerequisites: { completedTours: ["onboard.core"] },
  metadata: { estimatedMinutes: 4, priority: 80 },
  steps: [
    {
      id: "invoices-list",
      target: { kind: "tour", id: "sales-invoices-header" },
      presentation: "spotlight",
      content: {
        title: "Sales invoices",
        why: "Invoices drive revenue recognition and customer balances.",
        how: "Start here to create, approve, and track what customers owe you.",
      },
      placement: "bottom",
    },
    {
      id: "new-invoice",
      target: { kind: "tour", id: "sales-invoices-new" },
      presentation: "spotlight",
      content: {
        title: "Create an invoice",
        how: "Use **New invoice** to add header details and line items.",
        bestPractice: "Save as draft until totals and tax are verified.",
      },
      placement: "left",
    },
    {
      id: "invoice-grid",
      target: { kind: "grid", id: "sales-invoices-grid", rowIndex: 0 },
      presentation: "spotlight",
      content: {
        title: "Your invoice list",
        why: "Large lists stay fast with virtual scrolling.",
        how: "Click a row to open details. Use ↑↓ and Enter when the grid is focused.",
      },
      placement: "top",
      skippable: true,
    },
    {
      id: "customers",
      target: { kind: "tour", id: "sidebar-nav" },
      presentation: "panel",
      content: {
        title: "Customers",
        why: "Every invoice links to a customer for AR and statements.",
        how: "Under **Sell → Customers** maintain names, terms, and contacts.",
      },
    },
  ],
};
