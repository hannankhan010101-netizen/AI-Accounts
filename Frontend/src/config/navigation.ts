/**
 * Sidebar map — catalog §2.1 routes with task-based workspace labels (KISS IA).
 * href values are unchanged for catalog parity.
 */
import type { LucideIcon } from "lucide-react";
import {
  Banknote,
  BarChart3,
  BookOpen,
  Boxes,
  Home,
  Settings,
  ShoppingCart,
  Truck,
} from "lucide-react";

export interface NavItem {
  label: string;
  href: string;
  /** Shown on hover / screen readers when label differs from catalog name */
  catalogLabel?: string;
}

export interface NavGroup {
  label: string;
  icon: LucideIcon;
  href?: string;
  items?: NavItem[];
  /** Legacy catalog name for tooltips */
  catalogLabel?: string;
  /** Module code for RBAC module kill-switch filtering */
  moduleCode?: string;
}

export const navGroups: NavGroup[] = [
  { label: "Home", icon: Home, href: "/dashboard" },
  {
    label: "Sell",
    icon: ShoppingCart,
    moduleCode: "sales",
    items: [
      { label: "Invoices", href: "/sales/invoices", catalogLabel: "Sales Invoices" },
      { label: "Quotations", href: "/sales/quotations" },
      { label: "Orders", href: "/sales/orders", catalogLabel: "Sales Orders" },
      { label: "Credits", href: "/sales/credits", catalogLabel: "Sales Credits" },
      { label: "Receipts", href: "/sales/receipts", catalogLabel: "Sales Receipts" },
      { label: "Delivery notes", href: "/sales/delivery-notes", catalogLabel: "Delivery Notes" },
      {
        label: "Cheques received",
        href: "/sales/pdc-received",
        catalogLabel: "Post Dated Cheque Received",
      },
      { label: "All sales activity", href: "/sales/all", catalogLabel: "Sales All" },
      { label: "Customers", href: "/sales/customers" },
    ],
  },
  {
    label: "Buy",
    icon: Truck,
    moduleCode: "purchases",
    items: [
      { label: "Purchase orders", href: "/purchases/orders", catalogLabel: "PO" },
      { label: "Supplier bills", href: "/purchases/bills", catalogLabel: "Bills" },
      { label: "Credits", href: "/purchases/credits", catalogLabel: "Purchase Credits" },
      { label: "Payments", href: "/purchases/payments", catalogLabel: "Bill Payments" },
      {
        label: "Cheques issued",
        href: "/purchases/pdc-issued",
        catalogLabel: "Post Dated Cheque Issued",
      },
      { label: "Goods received", href: "/purchases/grn", catalogLabel: "GRN" },
      { label: "All purchase activity", href: "/purchases/all", catalogLabel: "Purchases All" },
      { label: "Suppliers", href: "/purchases/suppliers" },
    ],
  },
  {
    label: "Money",
    icon: Banknote,
    moduleCode: "bank",
    items: [
      { label: "Account balances", href: "/bank/balances", catalogLabel: "Account Balances" },
      { label: "Payments out", href: "/bank/payments", catalogLabel: "Bank Payments" },
      { label: "Receipts in", href: "/bank/receipts", catalogLabel: "Bank Receipts" },
      { label: "Transfers", href: "/bank/transfers" },
      { label: "Reconciliation", href: "/bank/reconciliation" },
      { label: "Import statement", href: "/bank/import-statement" },
      { label: "FX revaluation", href: "/bank/fx-revaluation", catalogLabel: "Revaluation" },
    ],
  },
  {
    label: "Stock",
    icon: Boxes,
    moduleCode: "inventory",
    items: [
      { label: "Products", href: "/inventory/products" },
      { label: "Stock adjustment", href: "/inventory/stock-adjustment" },
      { label: "Stock transfer", href: "/inventory/stock-transfer" },
      { label: "Batches and expiry", href: "/inventory/batches", catalogLabel: "Batches & Expiry" },
      { label: "Assembly templates", href: "/inventory/assembly/templates", catalogLabel: "Templates" },
      { label: "Assembly jobs", href: "/inventory/assembly/jobs", catalogLabel: "Jobs" },
    ],
  },
  {
    label: "Accounting",
    icon: BookOpen,
    moduleCode: "financial",
    items: [
      { label: "Journals", href: "/settings/journals" },
      { label: "Chart of accounts", href: "/settings/coa", catalogLabel: "Chart of Account" },
      { label: "Tax and year end", href: "/settings/taxes-year-end", catalogLabel: "Taxes and Year End" },
      { label: "Lock date", href: "/settings/lock-date" },
    ],
  },
  {
    label: "Insights",
    icon: BarChart3,
    moduleCode: "financial",
    items: [
      { label: "Reports", href: "/reports", catalogLabel: "Reports" },
      { label: "Analytical reports", href: "/reports/analytical", catalogLabel: "Analytical Reports" },
    ],
  },
  { label: "Admin", icon: Settings, href: "/admin" },
];
