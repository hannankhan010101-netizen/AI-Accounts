import type { DocumentLine, SalesInvoiceDetail, SupplierBillDetail } from "@/lib/api/tenant";
import { descriptionFieldsToFormLine } from "@/lib/hooks/product-description-columns";

export type GstLineFormRow = {
  productCode: string;
  quantity: string;
  rate: string;
  gstCode: string;
  gstRate: string;
  projectCode?: string;
  batchNumber?: string;
  expiryDate?: string;
  description?: string;
  text1?: string;
  text2?: string;
  text3?: string;
  text4?: string;
  text5?: string;
  text6?: string;
  [key: string]: string | undefined;
};

function isoDateOnly(value: string): string {
  return value.slice(0, 10);
}

function lineRate(value: string | number): string {
  return String(value);
}

export function salesInvoiceToFormValues(inv: SalesInvoiceDetail): {
  invoiceDate: string;
  customerId: string;
  lines: GstLineFormRow[];
} {
  return {
    invoiceDate: isoDateOnly(inv.invoiceDate),
    customerId: inv.customerId,
    lines:
      inv.lines.length > 0
        ? inv.lines.map((l) => ({
            productCode: l.productCode ?? "",
            quantity: lineRate(l.quantity),
            rate: lineRate(l.rate),
            gstCode: l.gstCode ?? "",
            gstRate: l.gstRate != null && l.gstRate !== "" ? lineRate(l.gstRate) : "",
            projectCode: l.projectCode ?? "",
            batchNumber: typeof l.batchNumber === "string" ? l.batchNumber : "",
            expiryDate:
              typeof l.expiryDate === "string" && l.expiryDate
                ? l.expiryDate.slice(0, 10)
                : "",
            ...descriptionFieldsToFormLine(l as Record<string, unknown>),
          }))
        : [
            {
              productCode: "",
              quantity: "1",
              rate: "0",
              gstCode: "",
              gstRate: "",
              projectCode: "",
              batchNumber: "",
              expiryDate: "",
            },
          ],
  };
}

export function supplierBillToFormValues(bill: SupplierBillDetail): {
  billDate: string;
  supplierId: string;
  lines: Omit<GstLineFormRow, "projectCode">[];
} {
  return {
    billDate: isoDateOnly(bill.billDate),
    supplierId: bill.supplierId,
    lines:
      bill.lines.length > 0
        ? bill.lines.map((l) => ({
            productCode: l.productCode ?? "",
            quantity: lineRate(l.quantity),
            rate: lineRate(l.rate),
            gstCode: l.gstCode ?? "",
            gstRate: l.gstRate != null && l.gstRate !== "" ? lineRate(l.gstRate) : "",
            batchNumber: typeof l.batchNumber === "string" ? l.batchNumber : "",
            expiryDate:
              typeof l.expiryDate === "string" && l.expiryDate
                ? l.expiryDate.slice(0, 10)
                : "",
            ...descriptionFieldsToFormLine(l as Record<string, unknown>),
          }))
        : [
            {
              productCode: "",
              quantity: "1",
              rate: "0",
              gstCode: "",
              gstRate: "",
              batchNumber: "",
              expiryDate: "",
            },
          ],
  };
}
