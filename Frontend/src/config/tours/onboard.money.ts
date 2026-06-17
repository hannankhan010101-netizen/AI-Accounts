import type { TourDefinition } from "@/lib/tour/types";

export const onboardMoneyTour: TourDefinition = {
  id: "onboard.money",
  version: 1,
  type: "onboard",
  title: "Money — bank accounts",
  module: "bank",
  personas: ["general", "accountant", "cfo", "admin"],
  prerequisites: { completedTours: ["onboard.core"] },
  metadata: { estimatedMinutes: 3, priority: 75 },
  steps: [
    {
      id: "balances",
      target: { kind: "tour", id: "bank-balances-header" },
      presentation: "spotlight",
      content: {
        title: "Bank accounts",
        why: "Cash activity rolls up to these accounts for reconciliation and reports.",
        how: "Review balances here before recording payments, receipts, or transfers.",
      },
      placement: "bottom",
    },
    {
      id: "add-account",
      target: { kind: "tour", id: "bank-balances-new" },
      presentation: "spotlight",
      content: {
        title: "Add a bank account",
        how: "Match your real-world account name and currency, then set an opening balance.",
      },
      placement: "left",
    },
    {
      id: "reconciliation",
      target: { kind: "tour", id: "sidebar-nav" },
      presentation: "panel",
      content: {
        title: "Reconciliation",
        why: "Reconciliation proves your books match the bank statement.",
        how: "Open **Money → Reconciliation** when you are ready to match transactions.",
      },
    },
  ],
};
