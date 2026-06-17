import type { TourDefinition } from "@/lib/tour/types";

export const workflowBankReceiptTour: TourDefinition = {
  id: "workflow.bank-receipt",
  version: 1,
  type: "workflow",
  title: "Record a bank receipt",
  module: "bank",
  personas: ["general", "accountant", "admin", "cfo"],
  prerequisites: {
    completedTours: ["onboard.core"],
    permissions: ["bank.payments.create"],
  },
  metadata: { estimatedMinutes: 4, priority: 67 },
  steps: [
    {
      id: "open-new",
      target: { kind: "tour", id: "bank-receipts-new" },
      presentation: "spotlight",
      content: {
        title: "New bank receipt",
        why: "Receipts record money in — refunds, capital, or other income.",
        how: "Click **Next →** to open the receipt form.",
      },
      placement: "left",
      action: { type: "navigate", href: "/bank/receipts/new" },
    },
    {
      id: "header",
      target: { kind: "tour", id: "br-new-header" },
      presentation: "spotlight",
      content: {
        title: "Receipt details",
        how: "Pick the **bank account**, **date**, and **amount**. Add a counterpart nominal if you want GL posting.",
      },
      placement: "bottom",
    },
    {
      id: "summary",
      target: { kind: "tour", id: "br-new-summary" },
      presentation: "spotlight",
      content: {
        title: "Summary",
        how: "Confirm the bank account and amount before saving.",
      },
      placement: "left",
    },
    {
      id: "save",
      target: { kind: "tour", id: "br-new-save" },
      presentation: "spotlight",
      content: {
        title: "Save receipt",
        how: "Click **Save receipt** to create the voucher.",
      },
      placement: "bottom",
      skippable: false,
    },
  ],
};
