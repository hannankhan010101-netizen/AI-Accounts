/** FA §12.1 OP (payment) methods — mirror Backend op_methods_catalog.py */

export type OpMethodDef = { id: string; label: string };

export const OP_METHOD_CATALOG: OpMethodDef[] = [
  { id: "cash", label: "Cash" },
  { id: "cheque", label: "Cheque" },
  { id: "pay_order", label: "Pay order" },
  { id: "demand_draft", label: "Demand draft" },
  { id: "bank_transfer", label: "Bank transfer / TT" },
  { id: "online", label: "Online payment" },
  { id: "credit_card", label: "Credit card" },
  { id: "pdc", label: "Post-dated cheque" },
];

export const DEFAULT_OP_METHOD_IDS = OP_METHOD_CATALOG.map((m) => m.id);

export function opMethodLabel(id: string): string {
  return OP_METHOD_CATALOG.find((m) => m.id === id)?.label ?? id;
}
