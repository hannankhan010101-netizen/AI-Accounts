import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const files = [
  "src/app/(app)/purchases/payments/page.tsx",
  "src/app/(app)/sales/receipts/page.tsx",
  "src/app/(app)/bank/payments/page.tsx",
  "src/app/(app)/bank/receipts/page.tsx",
  "src/app/(app)/settings/journals/page.tsx",
  "src/app/(app)/inventory/products/page.tsx",
  "src/app/(app)/purchases/bills/page.tsx",
  "src/app/(app)/bank/balances/page.tsx",
  "src/app/(app)/settings/import-jobs/page.tsx",
  "src/app/(app)/sales/quotations/page.tsx",
  "src/app/(app)/sales/pdc-received/page.tsx",
  "src/app/(app)/sales/orders/page.tsx",
  "src/app/(app)/sales/delivery-notes/page.tsx",
  "src/app/(app)/sales/customers/page.tsx",
  "src/app/(app)/sales/credits/page.tsx",
  "src/app/(app)/purchases/suppliers/page.tsx",
  "src/app/(app)/purchases/pdc-issued/page.tsx",
  "src/app/(app)/purchases/orders/page.tsx",
  "src/app/(app)/purchases/credits/page.tsx",
  "src/app/(app)/purchases/grn/page.tsx",
  "src/app/(app)/inventory/stock-transfer/page.tsx",
  "src/app/(app)/inventory/stock-adjustment/page.tsx",
  "src/app/(app)/bank/transfers/page.tsx",
  "src/app/(app)/inventory/batches/page.tsx",
];

const importLine =
  'import { responsiveListColumns } from "@/lib/grid/responsive-columns";\n';

for (const rel of files) {
  const f = path.join(root, rel);
  let s = fs.readFileSync(f, "utf8");
  if (s.includes("responsiveListColumns")) {
    console.log("skip", f);
    continue;
  }
  const next = s.replace(
    /const columns: GridColumn<(\w+)>\[\] = \[/g,
    "const columns = responsiveListColumns<$1>([",
  );
  if (next === s) {
    console.log("no match", f);
    continue;
  }
  s = next;
  if (!s.includes("@/lib/grid/responsive-columns")) {
    const m = s.match(/import.*enterprise-grid.*\n/);
    if (m) s = s.replace(m[0], m[0] + importLine);
  }
  fs.writeFileSync(f, s);
  console.log("ok", f);
}
