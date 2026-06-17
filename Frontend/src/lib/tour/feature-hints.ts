import { hasPermission } from "@/lib/rbac/permissions";
import type { FeatureHint, PersonaId, UserTourProgress } from "@/lib/tour/types";

const PERM_SALES = "sales.invoices.create";
const PERM_PURCHASES = "purchases.bills.create";
const PERM_BANK = "bank.payments.create";
const PERM_USERS = "settings.users.invite";

function tourStatus(progress: UserTourProgress, tourId: string) {
  return progress.tours[tourId]?.status ?? "not_started";
}

export function computeFeatureHints(ctx: {
  progress: UserTourProgress;
  permissions: string[];
  persona: PersonaId;
}): FeatureHint[] {
  const dismissed = new Set(ctx.progress.dismissedHints);
  const hints: FeatureHint[] = [];

  if (
    !dismissed.has("hint.welcome") &&
    tourStatus(ctx.progress, "onboard.core") !== "completed"
  ) {
    hints.push({
      id: "hint.welcome",
      title: "New here?",
      body: "Take a 3-minute tour of navigation, search, and your workspace.",
      ctaLabel: "Start welcome tour",
      tourId: "onboard.core",
      priority: 100,
    });
  }

  if (
    !dismissed.has("hint.sell") &&
    tourStatus(ctx.progress, "onboard.core") === "completed" &&
    tourStatus(ctx.progress, "onboard.sell") !== "completed" &&
    (hasPermission(ctx.permissions, PERM_SALES) || ctx.permissions.length === 0)
  ) {
    hints.push({
      id: "hint.sell",
      title: "Create your first invoice",
      body: "Learn the Sell workflow — customers, invoices, and receipts.",
      ctaLabel: "Sell tour",
      tourId: "onboard.sell",
      href: "/sales/invoices",
      priority: 90,
    });
  }

  if (
    !dismissed.has("hint.workflow-invoice") &&
    tourStatus(ctx.progress, "onboard.sell") === "completed" &&
    tourStatus(ctx.progress, "workflow.sales-invoice") !== "completed" &&
    hasPermission(ctx.permissions, PERM_SALES)
  ) {
    hints.push({
      id: "hint.workflow-invoice",
      title: "Walk through creating an invoice",
      body: "Step-by-step on the new invoice form — header, lines, and save.",
      ctaLabel: "Invoice workflow",
      tourId: "workflow.sales-invoice",
      href: "/sales/invoices",
      priority: 88,
    });
  }

  if (
    !dismissed.has("hint.workflow-sales-receipt") &&
    tourStatus(ctx.progress, "workflow.sales-invoice") === "completed" &&
    tourStatus(ctx.progress, "workflow.sales-receipt") !== "completed" &&
    hasPermission(ctx.permissions, PERM_SALES)
  ) {
    hints.push({
      id: "hint.workflow-sales-receipt",
      title: "Record a customer receipt",
      body: "Clear AR with FIFO or manual allocation to open invoices.",
      ctaLabel: "Receipt workflow",
      tourId: "workflow.sales-receipt",
      href: "/sales/receipts",
      priority: 86,
    });
  }

  if (
    !dismissed.has("hint.workflow-supplier-bill") &&
    tourStatus(ctx.progress, "onboard.buy") === "completed" &&
    tourStatus(ctx.progress, "workflow.supplier-bill") !== "completed" &&
    hasPermission(ctx.permissions, PERM_PURCHASES)
  ) {
    hints.push({
      id: "hint.workflow-supplier-bill",
      title: "Walk through creating a supplier bill",
      body: "Step-by-step on the new bill form — header, lines, and save.",
      ctaLabel: "Bill workflow",
      tourId: "workflow.supplier-bill",
      href: "/purchases/bills",
      priority: 87,
    });
  }

  if (
    !dismissed.has("hint.workflow-supplier-payment") &&
    tourStatus(ctx.progress, "workflow.supplier-bill") === "completed" &&
    tourStatus(ctx.progress, "workflow.supplier-payment") !== "completed" &&
    hasPermission(ctx.permissions, PERM_PURCHASES)
  ) {
    hints.push({
      id: "hint.workflow-supplier-payment",
      title: "Pay a supplier bill",
      body: "Clear AP with FIFO or manual allocation to open bills.",
      ctaLabel: "Payment workflow",
      tourId: "workflow.supplier-payment",
      href: "/purchases/payments",
      priority: 84,
    });
  }

  if (
    !dismissed.has("hint.money") &&
    tourStatus(ctx.progress, "onboard.core") === "completed" &&
    tourStatus(ctx.progress, "onboard.money") !== "completed" &&
    (hasPermission(ctx.permissions, PERM_BANK) || ctx.permissions.length === 0)
  ) {
    hints.push({
      id: "hint.money",
      title: "Set up bank accounts",
      body: "Connect cash activity to reconciliation and cash-flow reports.",
      ctaLabel: "Money tour",
      tourId: "onboard.money",
      href: "/bank/balances",
      priority: 85,
    });
  }

  if (
    !dismissed.has("hint.workflow-payment") &&
    tourStatus(ctx.progress, "onboard.money") === "completed" &&
    tourStatus(ctx.progress, "workflow.bank-payment") !== "completed" &&
    hasPermission(ctx.permissions, PERM_BANK)
  ) {
    hints.push({
      id: "hint.workflow-payment",
      title: "Record a bank payment",
      body: "Walk through paying out from a bank account.",
      ctaLabel: "Payment workflow",
      tourId: "workflow.bank-payment",
      href: "/bank/payments",
      priority: 82,
    });
  }

  if (
    !dismissed.has("hint.reconciliation") &&
    tourStatus(ctx.progress, "onboard.money") === "completed" &&
    (hasPermission(ctx.permissions, "bank.reconciliation.create") ||
      hasPermission(ctx.permissions, "bank.*") ||
      ctx.permissions.length === 0)
  ) {
    hints.push({
      id: "hint.reconciliation",
      title: "Did you know?",
      body: "Bank reconciliation matches your books to statements — fewer month-end surprises.",
      ctaLabel: "Open reconciliation",
      href: "/bank/reconciliation",
      priority: 70,
    });
  }

  if (
    !dismissed.has("hint.admin") &&
    ctx.persona === "admin" &&
    tourStatus(ctx.progress, "onboard.admin") !== "completed" &&
    hasPermission(ctx.permissions, PERM_USERS)
  ) {
    hints.push({
      id: "hint.admin",
      title: "Invite your team",
      body: "Assign roles so each person only sees what they need.",
      ctaLabel: "Team tour",
      tourId: "onboard.admin",
      href: "/settings/users",
      priority: 75,
    });
  }

  return hints;
}
