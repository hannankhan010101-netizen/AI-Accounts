"use client";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";



import { autoCodeApi } from "@/lib/api/tenant";


const TAX_ENTITIES = [
  { key: "gst", label: "GST" },
  { key: "adt", label: "ADT" },
  { key: "fed", label: "FED" },
  { key: "wht", label: "WHT" },
] as const;

export type TaxAutoCodeEntity = (typeof TAX_ENTITIES)[number]["key"];

export interface TaxAutoCodePeek {
  enabled: boolean;
  nextCode: string | null;
}

export function useTaxAutoCodePeek() {
  const gst = useTenantReferenceQuery(["auto-code-peek", "gst"], () => autoCodeApi.peek("gst"));
  const adt = useTenantReferenceQuery(["auto-code-peek", "adt"], () => autoCodeApi.peek("adt"));
  const fed = useTenantReferenceQuery(["auto-code-peek", "fed"], () => autoCodeApi.peek("fed"));
  const wht = useTenantReferenceQuery(["auto-code-peek", "wht"], () => autoCodeApi.peek("wht"));

  return {
    gst: gst.data?.result ?? { enabled: false, nextCode: null },
    adt: adt.data?.result ?? { enabled: false, nextCode: null },
    fed: fed.data?.result ?? { enabled: false, nextCode: null },
    wht: wht.data?.result ?? { enabled: false, nextCode: null },
  };
}

export function TaxAutoCodeHints({
  peek,
}: {
  peek: Record<TaxAutoCodeEntity, TaxAutoCodePeek>;
}) {
  const enabled = TAX_ENTITIES.some(({ key }) => peek[key]?.enabled);
  if (!enabled) return null;

  return (
    <section className="rounded-lg border border-border bg-canvas/40 p-4">
      <h2 className="mb-2 text-sm font-semibold text-fg">Tax auto codes</h2>
      <p className="mb-3 text-xs text-fg-muted">
        Next suggested codes from Smart Settings. Empty tax code fields are pre-filled when you add
        a row.
      </p>
      <div className="flex flex-wrap gap-4 text-sm">
        {TAX_ENTITIES.map(({ key, label }) => {
          const row = peek[key];
          if (!row?.enabled) return null;
          return (
            <div key={key}>
              <span className="text-fg-muted">{label}: </span>
              <span className="font-mono font-medium">{row.nextCode ?? "—"}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}
