import type { TourDefinition } from "@/lib/tour/types";

/** Guided create-invoice flow — list → new form → save. */
export const workflowSalesInvoiceTour: TourDefinition = {
  id: "workflow.sales-invoice",
  version: 1,
  type: "workflow",
  title: "Create a sales invoice",
  module: "sales",
  experience: "interactive",
  personas: ["general", "sales", "admin", "accountant"],
  prerequisites: {
    completedTours: ["onboard.core"],
    permissions: ["sales.invoices.create"],
  },
  metadata: { estimatedMinutes: 5, priority: 72 },
  steps: [
    {
      id: "nav-invoices",
      target: { kind: "tour", id: "nav-sales-invoices" },
      presentation: "spotlight",
      content: {
        title: "Sales invoices",
        why: "Every sale begins here.",
        how: "Opening **Sell → Invoices** for you.",
        assistantLine: "I'll take you to the invoice list first.",
      },
      enterAction: { type: "sidebarNavigate", href: "/sales/invoices", groupLabel: "Sell" },
      validation: { type: "routeMatch", pathname: "/sales/invoices" },
      autoContinue: true,
      autoContinueDelayMs: 1100,
      cursor: { enabled: true, clickPulse: true },
      placement: "right",
    },
    {
      id: "open-new",
      target: { kind: "tour", id: "sales-invoices-new" },
      presentation: "spotlight",
      content: {
        title: "Start a new invoice",
        why: "Every sale begins with header details and at least one line.",
        how: "Opening the new invoice form.",
        assistantLine: "Next we'll fill sample header and lines.",
      },
      placement: "left",
      enterAction: { type: "navigate", href: "/sales/invoices/new" },
      validation: { type: "routeMatch", pathname: "/sales/invoices/new" },
      autoContinue: true,
      autoContinueDelayMs: 1200,
      cursor: { enabled: true, clickPulse: true },
    },
    {
      id: "header",
      target: { kind: "tour", id: "si-new-header" },
      presentation: "spotlight",
      content: {
        title: "Header fields",
        how: "Pick the **customer** and **invoice date**. Both are required before save.",
        bestPractice: "Confirm the customer’s default terms on their profile if amounts look wrong.",
      },
      placement: "bottom",
    },
    {
      id: "lines",
      target: { kind: "tour", id: "si-new-lines" },
      presentation: "spotlight",
      content: {
        title: "Line items",
        how: "Add products or free-text lines with quantity, rate, and GST. Use **Add line** for more rows.",
      },
      placement: "top",
    },
    {
      id: "summary",
      target: { kind: "tour", id: "si-new-summary" },
      presentation: "spotlight",
      content: {
        title: "Live summary",
        why: "Totals update as you type — catch mistakes before posting.",
        how: "Review subtotal, tax, and grand total in the sticky panel.",
      },
      placement: "left",
    },
    {
      id: "save",
      target: { kind: "tour", id: "si-new-save" },
      presentation: "spotlight",
      content: {
        title: "Save when ready",
        how: "Click **Save invoice** to create the document. You can post or edit from the detail page next.",
      },
      placement: "bottom",
      skippable: false,
    },
  ],
};
