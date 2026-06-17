import type { CoaTreeCategory } from "@/lib/api/tenant";

export interface FlatNominalRow {
  id: string;
  code: string;
  name: string;
  description?: string | null;
  isChargeDeduction: boolean;
  categoryName: string;
  categoryType: string;
  sectionName: string;
  sectionCode: string;
  sectionId: string;
  [key: string]: unknown;
}

export function flattenCoaNominals(categories: CoaTreeCategory[]): FlatNominalRow[] {
  const out: FlatNominalRow[] = [];
  for (const cat of categories) {
    for (const sec of cat.sections) {
      for (const n of sec.nominals) {
        out.push({
          id: n.id,
          code: n.code,
          name: n.name,
          description: n.description,
          isChargeDeduction: n.isChargeDeduction,
          categoryName: cat.name,
          categoryType: cat.categoryType ?? "Other",
          sectionName: sec.name,
          sectionCode: sec.code,
          sectionId: sec.id,
        });
      }
    }
  }
  return out;
}
