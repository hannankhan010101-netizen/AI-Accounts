import type { TourDefinition } from "@/lib/tour/types";

export const workflowJournalTour: TourDefinition = {
  id: "workflow.journal",
  version: 1,
  type: "workflow",
  title: "Post a manual journal",
  module: "financial",
  personas: ["general", "accountant", "admin", "cfo"],
  prerequisites: {
    completedTours: ["onboard.core"],
    permissions: ["settings.journals.create"],
  },
  metadata: { estimatedMinutes: 5, priority: 68 },
  steps: [
    {
      id: "open-new",
      target: { kind: "tour", id: "journals-new" },
      presentation: "spotlight",
      content: {
        title: "New journal voucher",
        why: "Manual journals adjust GL outside sales and purchase documents.",
        how: "Click **Next →** to open the journal form.",
      },
      placement: "left",
      action: { type: "navigate", href: "/settings/journals/new" },
    },
    {
      id: "header",
      target: { kind: "tour", id: "journal-new-header" },
      presentation: "spotlight",
      content: {
        title: "Journal header",
        how: "Set the **journal date** and an optional **reference** for audit trails.",
      },
      placement: "bottom",
    },
    {
      id: "lines",
      target: { kind: "tour", id: "journal-new-lines" },
      presentation: "spotlight",
      content: {
        title: "Debit and credit lines",
        how: "Enter nominal codes with amounts on the debit or credit side. Add lines until debits equal credits.",
        bestPractice: "Use at least two lines — every journal must balance to zero.",
      },
      placement: "top",
    },
    {
      id: "balance",
      target: { kind: "tour", id: "journal-new-summary" },
      presentation: "spotlight",
      content: {
        title: "Balance check",
        why: "Unbalanced journals cannot post.",
        how: "Watch the difference row — it must show balanced before you save.",
      },
      placement: "left",
    },
    {
      id: "save",
      target: { kind: "tour", id: "journal-new-save" },
      presentation: "spotlight",
      content: {
        title: "Post when balanced",
        how: "Click **Post journal** when debit and credit totals match.",
      },
      placement: "bottom",
      skippable: false,
    },
  ],
};
