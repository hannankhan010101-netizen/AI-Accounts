/** Print template codes — mirror Backend print_template_catalog.py */

export interface PrintTemplateMeta {
  code: string;
  label: string;
  group: string;
  supportsTwoCopies?: boolean;
  printModes?: string[];
}

export const PRINT_TEMPLATE_CATALOG: PrintTemplateMeta[] = [
  { code: "si", label: "Sales Invoice (SI)", group: "Sales Printing" },
  { code: "sc", label: "Sales Credit (SC)", group: "Sales Printing" },
  { code: "so", label: "Sales Order (SO)", group: "Sales Printing" },
  { code: "sr", label: "Sales Receipt (SR)", group: "Sales Printing", supportsTwoCopies: true },
  { code: "pdcr", label: "Post Dated Cheque Received (PDCR)", group: "Sales Printing" },
  { code: "gdnso", label: "Delivery Note from SO (GDNSO)", group: "Sales Printing" },
  { code: "gdnsi", label: "Delivery Note from SI (GDNSI)", group: "Sales Printing" },
  { code: "cus", label: "Customer (CUS)", group: "Sales Printing" },
  { code: "vi", label: "Supplier Bill (VI)", group: "Purchases Printing" },
  { code: "vc", label: "Supplier Credit (VC)", group: "Purchases Printing" },
  { code: "po", label: "Purchase Order (PO)", group: "Purchases Printing" },
  { code: "vp", label: "Bill Payment (VP)", group: "Purchases Printing", supportsTwoCopies: true },
  { code: "pdci", label: "Post Dated Cheque Issued (PDCI)", group: "Purchases Printing" },
  { code: "grnpo", label: "GRN from PO (GRNPO)", group: "Purchases Printing" },
  { code: "grnvi", label: "GRN from VI (GRNVI)", group: "Purchases Printing" },
  { code: "journal", label: "Journal", group: "Journal / Bank / Other / Project Printing" },
  {
    code: "bank",
    label: "Bank voucher",
    group: "Journal / Bank / Other / Project Printing",
    printModes: ["voucher", "journal"],
  },
  { code: "assembly", label: "Assembly", group: "Journal / Bank / Other / Project Printing" },
  { code: "stock-adjustment", label: "Stock Adjustment", group: "Journal / Bank / Other / Project Printing" },
  { code: "stock-transfer", label: "Stock Transfer", group: "Journal / Bank / Other / Project Printing" },
  { code: "user-log", label: "User Log", group: "Journal / Bank / Other / Project Printing" },
  { code: "project", label: "Project", group: "Journal / Bank / Other / Project Printing" },
];

export const PRINT_TEMPLATE_BY_CODE = Object.fromEntries(
  PRINT_TEMPLATE_CATALOG.map((t) => [t.code, t]),
) as Record<string, PrintTemplateMeta>;

export function printTemplateMeta(code: string): PrintTemplateMeta | undefined {
  return PRINT_TEMPLATE_BY_CODE[code];
}
