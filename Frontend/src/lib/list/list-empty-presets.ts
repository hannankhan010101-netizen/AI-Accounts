import type { LucideIcon } from "lucide-react";
import {
  FileText,
  Package,
  Receipt,
  ShoppingCart,
  Truck,
  Users,
} from "lucide-react";

export type ListEntityKey =
  | "sales-invoice"
  | "sales-quotation"
  | "sales-order"
  | "sales-credit"
  | "sales-receipt"
  | "sales-delivery-note"
  | "sales-pdc-received"
  | "sales-customer"
  | "sales-activity"
  | "purchase-order"
  | "purchase-bill"
  | "purchase-credit"
  | "purchase-payment"
  | "purchase-pdc-issued"
  | "purchase-grn"
  | "purchase-supplier"
  | "purchase-activity"
  | "bank-receipt"
  | "bank-payment"
  | "bank-transfer";

export type ListEmptyPreset = {
  icon: LucideIcon;
  title: string;
  emptyDescription: string;
  searchDescription: string;
  createHref?: string;
  createLabel?: string;
};

export const LIST_EMPTY_PRESETS: Record<ListEntityKey, ListEmptyPreset> = {
  "sales-invoice": {
    icon: FileText,
    title: "No invoices yet",
    emptyDescription: "Create your first sales invoice to start billing customers.",
    searchDescription: "No invoices match your search.",
    createHref: "/sales/invoices/new",
    createLabel: "New invoice",
  },
  "sales-quotation": {
    icon: FileText,
    title: "No quotations yet",
    emptyDescription: "Send a quotation before converting it to an order or invoice.",
    searchDescription: "No quotations match your search.",
    createHref: "/sales/quotations/new",
    createLabel: "New quotation",
  },
  "sales-order": {
    icon: ShoppingCart,
    title: "No sales orders yet",
    emptyDescription: "Track customer orders before invoicing or delivery.",
    searchDescription: "No orders match your search.",
    createHref: "/sales/orders/new",
    createLabel: "New order",
  },
  "sales-credit": {
    icon: Receipt,
    title: "No sales credits yet",
    emptyDescription: "Issue a credit note when you need to adjust a customer balance.",
    searchDescription: "No credits match your search.",
    createHref: "/sales/credits/new",
    createLabel: "New credit",
  },
  "sales-receipt": {
    icon: Receipt,
    title: "No receipts yet",
    emptyDescription: "Record customer payments against open invoices.",
    searchDescription: "No receipts match your search.",
    createHref: "/sales/receipts/new",
    createLabel: "New receipt",
  },
  "sales-delivery-note": {
    icon: Truck,
    title: "No delivery notes yet",
    emptyDescription: "Create delivery notes when goods leave your warehouse.",
    searchDescription: "No delivery notes match your search.",
    createHref: "/sales/delivery-notes/new",
    createLabel: "New delivery note",
  },
  "sales-pdc-received": {
    icon: Receipt,
    title: "No cheques received yet",
    emptyDescription: "Track post-dated cheques received from customers.",
    searchDescription: "No cheques match your search.",
    createHref: "/sales/pdc-received/new",
    createLabel: "New cheque",
  },
  "sales-customer": {
    icon: Users,
    title: "No customers yet",
    emptyDescription: "Add customers before creating invoices or receipts.",
    searchDescription: "No customers match your search.",
    createHref: "/sales/customers/new",
    createLabel: "New customer",
  },
  "sales-activity": {
    icon: ShoppingCart,
    title: "No sales activity",
    emptyDescription: "Sales documents will appear here as you create them.",
    searchDescription: "No activity matches your search.",
  },
  "purchase-order": {
    icon: ShoppingCart,
    title: "No purchase orders yet",
    emptyDescription: "Raise POs before receiving goods or supplier bills.",
    searchDescription: "No purchase orders match your search.",
    createHref: "/purchases/orders/new",
    createLabel: "New PO",
  },
  "purchase-bill": {
    icon: FileText,
    title: "No supplier bills yet",
    emptyDescription: "Record supplier bills to track payables.",
    searchDescription: "No bills match your search.",
    createHref: "/purchases/bills/new",
    createLabel: "New bill",
  },
  "purchase-credit": {
    icon: Receipt,
    title: "No purchase credits yet",
    emptyDescription: "Issue credits when suppliers adjust your balance.",
    searchDescription: "No credits match your search.",
    createHref: "/purchases/credits/new",
    createLabel: "New credit",
  },
  "purchase-payment": {
    icon: Receipt,
    title: "No payments yet",
    emptyDescription: "Pay supplier bills and track outgoing cash.",
    searchDescription: "No payments match your search.",
    createHref: "/purchases/payments/new",
    createLabel: "New payment",
  },
  "purchase-pdc-issued": {
    icon: Receipt,
    title: "No cheques issued yet",
    emptyDescription: "Track post-dated cheques issued to suppliers.",
    searchDescription: "No cheques match your search.",
    createHref: "/purchases/pdc-issued/new",
    createLabel: "New cheque",
  },
  "purchase-grn": {
    icon: Package,
    title: "No GRNs yet",
    emptyDescription: "Record goods received against purchase orders.",
    searchDescription: "No GRNs match your search.",
    createHref: "/purchases/grn/new",
    createLabel: "New GRN",
  },
  "purchase-supplier": {
    icon: Users,
    title: "No suppliers yet",
    emptyDescription: "Add suppliers before creating bills or payments.",
    searchDescription: "No suppliers match your search.",
    createHref: "/purchases/suppliers/new",
    createLabel: "New supplier",
  },
  "purchase-activity": {
    icon: Truck,
    title: "No purchase activity",
    emptyDescription: "Purchase documents will appear here as you create them.",
    searchDescription: "No activity matches your search.",
  },
  "bank-receipt": {
    icon: Receipt,
    title: "No bank receipts yet",
    emptyDescription: "Record money received into your bank accounts.",
    searchDescription: "No receipts match your search.",
    createHref: "/bank/receipts/new",
    createLabel: "New receipt",
  },
  "bank-payment": {
    icon: Receipt,
    title: "No bank payments yet",
    emptyDescription: "Record outgoing payments from your bank accounts.",
    searchDescription: "No payments match your search.",
    createHref: "/bank/payments/new",
    createLabel: "New payment",
  },
  "bank-transfer": {
    icon: Receipt,
    title: "No transfers yet",
    emptyDescription: "Move funds between bank accounts or cash books.",
    searchDescription: "No transfers match your search.",
    createHref: "/bank/transfers/new",
    createLabel: "New transfer",
  },
};

export function resolveListEmpty(
  entity: ListEntityKey,
  searching: boolean,
): Pick<ListEmptyPreset, "icon" | "createHref" | "createLabel"> & {
  title?: string;
  description: string;
} {
  const preset = LIST_EMPTY_PRESETS[entity];
  return {
    icon: preset.icon,
    title: searching ? undefined : preset.title,
    description: searching ? preset.searchDescription : preset.emptyDescription,
    createHref: preset.createHref,
    createLabel: preset.createLabel,
  };
}
