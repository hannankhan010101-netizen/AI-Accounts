import type { TourDefinition } from "@/lib/tour/types";

export const workflowSupplierPaymentTour: TourDefinition = {
  id: "workflow.supplier-payment",
  version: 1,
  type: "workflow",
  title: "Pay a supplier bill",
  module: "purchases",
  personas: ["general", "procurement", "admin", "accountant"],
  prerequisites: {
    completedTours: ["onboard.core"],
    permissions: ["purchases.bills.create"],
  },
  metadata: { estimatedMinutes: 5, priority: 64 },
  steps: [
    {
      id: "open-new",
      target: { kind: "tour", id: "supplier-payments-new" },
      presentation: "spotlight",
      content: {
        title: "New bill payment",
        why: "Payments clear AP and can auto-allocate to open supplier bills.",
        how: "Click **Next →** to open the payment form.",
      },
      placement: "left",
      action: { type: "navigate", href: "/purchases/payments/new" },
    },
    {
      id: "header",
      target: { kind: "tour", id: "vp-new-header" },
      presentation: "spotlight",
      content: {
        title: "Payment header",
        how: "Select **supplier**, **bank account**, **date**, and **amount**.",
      },
      placement: "bottom",
    },
    {
      id: "allocate",
      target: { kind: "tour", id: "vp-new-alloc" },
      presentation: "spotlight",
      content: {
        title: "Allocate to bills",
        why: "Linking a payment to bills keeps AP accurate.",
        how: "Leave **FIFO** checked for automatic allocation, or uncheck to pick bills manually.",
        bestPractice: "FIFO applies to the oldest open bills first.",
      },
      placement: "top",
      skippable: true,
    },
    {
      id: "summary",
      target: { kind: "tour", id: "vp-new-summary" },
      presentation: "spotlight",
      content: {
        title: "Summary",
        how: "Confirm supplier, bank, and allocation mode before saving.",
      },
      placement: "left",
    },
    {
      id: "save",
      target: { kind: "tour", id: "vp-new-save" },
      presentation: "spotlight",
      content: {
        title: "Save payment",
        how: "Click **Save payment** to post cash and update supplier balance.",
      },
      placement: "bottom",
      skippable: false,
    },
  ],
};
