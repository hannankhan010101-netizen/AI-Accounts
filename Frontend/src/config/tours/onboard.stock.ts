import type { TourDefinition } from "@/lib/tour/types";

export const onboardStockTour: TourDefinition = {
  id: "onboard.stock",
  version: 1,
  type: "module",
  title: "Stock — products & inventory",
  module: "inventory",
  personas: ["general", "inventory_manager", "admin", "accountant"],
  prerequisites: { completedTours: ["onboard.core"] },
  metadata: { estimatedMinutes: 3, priority: 75 },
  steps: [
    {
      id: "products-header",
      target: { kind: "tour", id: "inventory-products-header" },
      presentation: "spotlight",
      content: {
        title: "Product catalog",
        why: "Products drive costing on invoices, bills, and stock movements.",
        how: "Maintain codes, units, and prices here before posting transactions.",
      },
      placement: "bottom",
    },
    {
      id: "add-product",
      target: { kind: "tour", id: "inventory-products-new" },
      presentation: "spotlight",
      content: {
        title: "Add a product",
        how: "Use **Add product** for new SKUs. Keep codes short and unique.",
      },
      placement: "left",
    },
    {
      id: "products-grid",
      target: { kind: "grid", id: "inventory-products-grid", rowIndex: 0 },
      presentation: "spotlight",
      content: {
        title: "Browse products",
        why: "Large catalogs stay responsive with virtual scrolling.",
        how: "Open a row for details. Export CSV from the grid when needed.",
      },
      placement: "top",
      skippable: true,
    },
    {
      id: "stock-tasks",
      target: { kind: "tour", id: "sidebar-nav" },
      presentation: "panel",
      content: {
        title: "Adjustments & transfers",
        how: "Under **Stock**, use adjustments for corrections and transfers between locations.",
      },
    },
  ],
};
