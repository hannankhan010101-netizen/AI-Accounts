import type { TourDemoPreview } from "@/lib/tour/types";

/** Realistic sample payloads for interactive demo cards (no API writes). */
export const DEMO_PREVIEWS: Record<string, TourDemoPreview> = {
  "invoice-acme": {
    id: "invoice-acme",
    headline: "Sample invoice — Acme Trading Co.",
    badge: "Demo data",
    lines: [
      "Customer: Acme Trading Co.",
      "Date: 22 May 2026",
      "Line 1: Consulting services · Qty 10 × ₹4,500",
      "GST 18% · Total ₹53,100",
    ],
  },
  "receipt-payment": {
    id: "receipt-payment",
    headline: "Customer payment — Acme Trading Co.",
    badge: "Practice",
    lines: [
      "Amount received: ₹53,100",
      "Allocated to INV-1042",
      "Bank: HDFC Current · ****4821",
    ],
  },
  "supplier-bill": {
    id: "supplier-bill",
    headline: "Supplier bill — Nova Supplies",
    badge: "Demo data",
    lines: [
      "Supplier: Nova Supplies Pvt Ltd",
      "Bill date: 20 May 2026",
      "Inventory items · ₹28,400 + GST",
    ],
  },
  "bank-recon": {
    id: "bank-recon",
    headline: "May statement vs books",
    badge: "Sandbox",
    lines: [
      "3 unmatched deposits",
      "1 missing payment",
      "Suggested match: ₹12,500 transfer",
    ],
  },
  "stock-adjust": {
    id: "stock-adjust",
    headline: "Stock adjustment — Widget A",
    badge: "Demo data",
    lines: [
      "Warehouse: Main",
      "Counted: 142 · System: 138",
      "Adjustment: +4 units",
    ],
  },
  "dashboard-kpis": {
    id: "dashboard-kpis",
    headline: "This month at a glance",
    badge: "Illustrative",
    lines: [
      "Revenue ↑ 12% vs last month",
      "Outstanding AR: ₹4.2L",
      "Cash on hand: ₹18.6L",
    ],
  },
  "report-pl": {
    id: "report-pl",
    headline: "Profit & Loss — May 2026",
    badge: "Demo data",
    lines: [
      "Revenue: ₹12.4L",
      "COGS: ₹6.1L",
      "Net profit: ₹2.8L",
    ],
  },
  "assembly-job": {
    id: "assembly-job",
    headline: "Assembly job — Kit BOM-12",
    badge: "Concept demo",
    lines: [
      "Finished good: Widget Kit",
      "Components issued from stock",
      "Labour + overhead absorbed on completion",
    ],
  },
};

export function getDemoPreview(id: string | undefined): TourDemoPreview | null {
  if (!id) return null;
  return DEMO_PREVIEWS[id] ?? null;
}
