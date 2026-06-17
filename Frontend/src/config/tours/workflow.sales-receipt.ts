import type { TourDefinition } from "@/lib/tour/types";

export const workflowSalesReceiptTour: TourDefinition = {
  id: "workflow.sales-receipt",
  version: 1,
  type: "workflow",
  title: "Record a customer receipt",
  module: "sales",
  personas: ["general", "sales", "admin", "accountant"],
  prerequisites: {
    completedTours: ["onboard.core"],
    permissions: ["sales.invoices.create"],
  },
  metadata: { estimatedMinutes: 5, priority: 65 },
  steps: [
    {
      id: "open-new",
      target: { kind: "tour", id: "sales-receipts-new" },
      presentation: "spotlight",
      content: {
        title: "New customer receipt",
        why: "Receipts clear AR and can auto-allocate to open invoices.",
        how: "Click **Next →** to open the receipt form.",
      },
      placement: "left",
      action: { type: "navigate", href: "/sales/receipts/new" },
    },
    {
      id: "header",
      target: { kind: "tour", id: "sr-new-header" },
      presentation: "spotlight",
      content: {
        title: "Receipt header",
        how: "Select **customer**, **bank account**, **date**, and **amount**.",
      },
      placement: "bottom",
    },
    {
      id: "allocate",
      target: { kind: "tour", id: "sr-new-alloc" },
      presentation: "spotlight",
      content: {
        title: "Allocate to invoices",
        why: "Linking a receipt to invoices keeps AR accurate.",
        how: "Leave **FIFO** checked for automatic allocation, or uncheck to pick invoices manually.",
        bestPractice: "FIFO applies to the oldest open invoices first.",
      },
      placement: "top",
      skippable: true,
    },
    {
      id: "summary",
      target: { kind: "tour", id: "sr-new-summary" },
      presentation: "spotlight",
      content: {
        title: "Summary",
        how: "Confirm customer, bank, and allocation mode before saving.",
      },
      placement: "left",
    },
    {
      id: "save",
      target: { kind: "tour", id: "sr-new-save" },
      presentation: "spotlight",
      content: {
        title: "Save receipt",
        how: "Click **Save receipt** to post cash and update customer balance.",
      },
      placement: "bottom",
      skippable: false,
    },
  ],
};
