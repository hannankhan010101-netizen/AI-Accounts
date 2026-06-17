type DraftLine = { rate?: string; productCode?: string; quantity?: string };

/** True when a line-grid document has party or line content worth autosaving. */
export function hasMeaningfulLineGridDraft(values: {
  partyId?: string;
  customerId?: string;
  supplierId?: string;
  lines?: DraftLine[];
}): boolean {
  const party = values.partyId ?? values.customerId ?? values.supplierId;
  return (
    Boolean(party) ||
    Boolean(
      values.lines?.some((l) => l.rate !== "0" || l.productCode || l.quantity !== "1"),
    )
  );
}

/** True when a simple master form has any field filled. */
export function hasMeaningfulMasterDraft(values: Record<string, unknown>): boolean {
  return Object.values(values).some((v) => {
    if (typeof v === "boolean") return v !== true;
    if (typeof v === "string") return v.trim().length > 0;
    return v != null && v !== "";
  });
}
