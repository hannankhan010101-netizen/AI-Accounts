import type { TourDefinition } from "@/lib/tour/types";

type TourLoader = () => Promise<TourDefinition>;

/** Code-split tour definitions — loaded on demand. */
export const LAZY_TOUR_LOADERS: Record<string, TourLoader> = {
  "onboard.sell": () =>
    import("@/config/tours/onboard.sell").then((m) => m.onboardSellTour),
  "onboard.money": () =>
    import("@/config/tours/onboard.money").then((m) => m.onboardMoneyTour),
  "onboard.buy": () =>
    import("@/config/tours/onboard.buy").then((m) => m.onboardBuyTour),
  "onboard.admin": () =>
    import("@/config/tours/onboard.admin").then((m) => m.onboardAdminTour),
  "onboard.stock": () =>
    import("@/config/tours/onboard.stock").then((m) => m.onboardStockTour),
  "onboard.reports": () =>
    import("@/config/tours/onboard.reports").then((m) => m.onboardReportsTour),
  "release.invoice-void": () =>
    import("@/config/tours/release.invoice-void").then((m) => m.releaseInvoiceVoidTour),
  "release.bank-recon": () =>
    import("@/config/tours/release.bank-recon").then((m) => m.releaseBankReconTour),
  "workflow.sales-invoice": () =>
    import("@/config/tours/workflow.sales-invoice").then((m) => m.workflowSalesInvoiceTour),
  "workflow.sales-receipt": () =>
    import("@/config/tours/workflow.sales-receipt").then((m) => m.workflowSalesReceiptTour),
  "workflow.supplier-bill": () =>
    import("@/config/tours/workflow.supplier-bill").then((m) => m.workflowSupplierBillTour),
  "workflow.supplier-payment": () =>
    import("@/config/tours/workflow.supplier-payment").then((m) => m.workflowSupplierPaymentTour),
  "workflow.journal": () =>
    import("@/config/tours/workflow.journal").then((m) => m.workflowJournalTour),
  "workflow.bank-receipt": () =>
    import("@/config/tours/workflow.bank-receipt").then((m) => m.workflowBankReceiptTour),
  "workflow.bank-payment": () =>
    import("@/config/tours/workflow.bank-payment").then((m) => m.workflowBankPaymentTour),
  "demo.sales-invoice": () =>
    import("@/config/tours/demo-workflows").then((m) => m.demoSalesInvoiceTour),
  "demo.bank-recon": () =>
    import("@/config/tours/demo-workflows").then((m) => m.demoBankReconTour),
  "demo.purchase-bill": () =>
    import("@/config/tours/demo-workflows").then((m) => m.demoPurchaseBillTour),
  "demo.inventory-adjust": () =>
    import("@/config/tours/demo-workflows").then((m) => m.demoInventoryAdjustTour),
  "demo.customer-payment": () =>
    import("@/config/tours/demo-workflows").then((m) => m.demoCustomerPaymentTour),
  "demo.dashboard": () =>
    import("@/config/tours/demo-workflows").then((m) => m.demoDashboardTour),
  "demo.reports": () =>
    import("@/config/tours/demo-workflows").then((m) => m.demoReportsTour),
  "demo.assembly": () =>
    import("@/config/tours/demo-workflows").then((m) => m.demoAssemblyTour),
  "demo.bank-receipt": () =>
    import("@/config/tours/demo-workflows").then((m) => m.demoBankReceiptTour),
  "demo.bank-payment": () =>
    import("@/config/tours/demo-workflows").then((m) => m.demoBankPaymentTour),
  "demo.supplier-payment": () =>
    import("@/config/tours/demo-workflows").then((m) => m.demoSupplierPaymentTour),
};

const pending = new Map<string, Promise<TourDefinition | undefined>>();

export function registerTourDefinition(
  registry: Map<string, TourDefinition>,
  list: TourDefinition[],
  def: TourDefinition,
): void {
  if (!registry.has(def.id)) {
    registry.set(def.id, def);
    list.push(def);
  }
}

/** Load a tour chunk and register it in the in-memory registry. */
export function preloadTour(
  tourId: string,
  registry: Map<string, TourDefinition>,
  list: TourDefinition[],
): Promise<TourDefinition | undefined> {
  if (registry.has(tourId)) return Promise.resolve(registry.get(tourId));
  const existing = pending.get(tourId);
  if (existing) return existing;

  const loader = LAZY_TOUR_LOADERS[tourId];
  if (!loader) return Promise.resolve(undefined);

  const promise = loader()
    .then((def) => {
      registerTourDefinition(registry, list, def);
      pending.delete(tourId);
      return def;
    })
    .catch(() => {
      pending.delete(tourId);
      return undefined;
    });

  pending.set(tourId, promise);
  return promise;
}

export function preloadToursForPath(
  pathname: string,
  tourIds: string[],
  registry: Map<string, TourDefinition>,
  list: TourDefinition[],
): void {
  for (const id of tourIds) {
    void preloadTour(id, registry, list);
  }
  if (pathname.startsWith("/sales")) {
    void preloadTour("workflow.sales-invoice", registry, list);
    void preloadTour("workflow.sales-receipt", registry, list);
  }
}
