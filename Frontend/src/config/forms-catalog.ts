/** Content Settings form targets — catalog §12.14 Forms branch */

export interface FormMeta {
  id: string;
  label: string;
  branch: string;
}

export const FORM_CATALOG: FormMeta[] = [
  { id: "sales-invoice", label: "Sales invoice form", branch: "Sales Forms" },
  { id: "sales-receipt", label: "Sales receipt form", branch: "Sales Forms" },
  { id: "supplier-bill", label: "Supplier bill form", branch: "Purchase Forms" },
  { id: "supplier-payment", label: "Supplier payment form", branch: "Purchase Forms" },
  { id: "bank-payment", label: "Bank payment form", branch: "Bank Forms" },
];

export const FORM_BRANCHES = [...new Set(FORM_CATALOG.map((f) => f.branch))];

export function formsForBranch(branch: string): FormMeta[] {
  return FORM_CATALOG.filter((f) => f.branch === branch);
}
