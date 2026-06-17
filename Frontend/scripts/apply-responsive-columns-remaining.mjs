import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const importLine =
  'import { responsiveListColumns } from "@/lib/grid/responsive-columns";\n';

const files = [
  "src/app/(app)/bank/reconciliation/page.tsx",
  "src/app/(app)/inventory/stock-adjustment/[id]/page.tsx",
  "src/app/(app)/inventory/stock-transfer/[id]/page.tsx",
  "src/app/(app)/settings/journals/[id]/page.tsx",
  "src/components/app/statement-report.tsx",
  "src/components/app/aging-report.tsx",
  "src/app/(app)/settings/module-access/page.tsx",
  "src/app/(app)/settings/custom-fields/page.tsx",
  "src/app/(app)/settings/sections/page.tsx",
  "src/components/patterns/logistics-document-detail.tsx",
  "src/components/reports/financial-report-block.tsx",
  "src/components/patterns/document-lines-grid.tsx",
  "src/components/settings/coa-nominal-grid.tsx",
  "src/components/reports/dynamic-report-grid.tsx",
];

function ensureImport(s) {
  if (s.includes("@/lib/grid/responsive-columns")) return s;
  const m = s.match(/import.*enterprise-grid.*\n/);
  if (m) return s.replace(m[0], m[0] + importLine);
  return importLine + s;
}

for (const rel of files) {
  const f = path.join(root, rel);
  if (!fs.existsSync(f)) {
    console.log("missing", rel);
    continue;
  }
  let s = fs.readFileSync(f, "utf8");
  if (s.includes("responsiveListColumns")) {
    console.log("skip", rel);
    continue;
  }

  let next = s;

  // useMemo(() => [  -> useMemo(() => responsiveListColumns<T>([
  next = next.replace(
    /const columns: GridColumn<(\w+)>\[\] = useMemo\(\s*\n?\s*\(\) => \[/g,
    "const columns = useMemo(\n    () => responsiveListColumns<$1>([",
  );
  next = next.replace(
    /const columns: GridColumn<(\w+)>\[\] = useMemo\(\s*\(\) => \[/g,
    "const columns = useMemo(() => responsiveListColumns<$1>([",
  );

  // plain array
  next = next.replace(
    /const columns: GridColumn<(\w+)>\[\] = \[/g,
    "const columns = responsiveListColumns<$1>([",
  );

  if (next === s) {
    console.log("no match", rel);
    continue;
  }

  // Fix useMemo closing: `],\n    [deps]` -> `]),\n    [deps]` when responsiveListColumns used in useMemo
  if (next.includes("useMemo") && next.includes("responsiveListColumns")) {
    next = next.replace(
      /(\s+)\],\s*\n(\s+)\[([^\]]*)\],\s*\n(\s+)\);/g,
      "$1]),\n$2[$3],\n$4);",
    );
    // simpler: ],\n    [bankNames] -> ]),\n    [bankNames]
    next = next.replace(
      /(\]\s*,)\s*\n(\s+)\[([^\]]+)\]\s*,\s*\n(\s+)\)/g,
      (match, _a, indent, deps, close) => {
        if (match.includes("responsiveListColumns")) {
          return `]),\n${indent}[${deps}],\n${close}`;
        }
        return match;
      },
    );
  }

  // Plain closing ]; -> ]);
  if (!next.includes("useMemo(() => responsiveListColumns")) {
    next = next.replace(
      /(responsiveListColumns<\w+>\(\[[\s\S]*?)\n  \];/,
      "$1\n  ]);",
    );
  }

  s = ensureImport(next);
  fs.writeFileSync(f, s);
  console.log("ok", rel);
}
