import type { TourDefinition } from "@/lib/tour/types";

export const workflowBankPaymentTour: TourDefinition = {
  id: "workflow.bank-payment",
  version: 1,
  type: "workflow",
  title: "Record a bank payment",
  module: "bank",
  personas: ["general", "accountant", "admin", "cfo"],
  prerequisites: {
    completedTours: ["onboard.core"],
    permissions: ["bank.payments.create"],
  },
  metadata: { estimatedMinutes: 4, priority: 66 },
  steps: [
    {
      id: "open-new",
      target: { kind: "tour", id: "bank-payments-new" },
      presentation: "spotlight",
      content: {
        title: "New bank payment",
        why: "Payments out reduce bank balance and can post to expense nominals.",
        how: "Click **Next →** to open the payment form.",
      },
      placement: "left",
      action: { type: "navigate", href: "/bank/payments/new" },
    },
    {
      id: "header",
      target: { kind: "tour", id: "bp-new-header" },
      presentation: "spotlight",
      content: {
        title: "Payment details",
        how: "Choose **bank account**, **date**, and **amount**. Optional nominal overrides the default expense account.",
      },
      placement: "bottom",
    },
    {
      id: "summary",
      target: { kind: "tour", id: "bp-new-summary" },
      presentation: "spotlight",
      content: {
        title: "Summary",
        how: "Verify account and amount before saving.",
      },
      placement: "left",
    },
    {
      id: "save",
      target: { kind: "tour", id: "bp-new-save" },
      presentation: "spotlight",
      content: {
        title: "Save payment",
        how: "Click **Save payment** to create the voucher.",
      },
      placement: "bottom",
      skippable: false,
    },
  ],
};
