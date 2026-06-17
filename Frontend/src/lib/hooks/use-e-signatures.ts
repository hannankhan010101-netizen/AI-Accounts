"use client";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";



import { settingsApi } from "@/lib/api/tenant";


export interface ESignatureRow {
  name: string;
  signatureUrl?: string | null;
}

export function useESignatures() {
  const { data, isLoading } = useTenantReferenceQuery(["smart-settings"], () => settingsApi.getSmartSettings());

  const raw = data?.result?.payload?.eSignatures;
  const eSignatures: ESignatureRow[] = Array.isArray(raw)
    ? raw.flatMap((row) => {
        if (!row || typeof row !== "object") return [];
        const name = "name" in row ? String(row.name ?? "").trim() : "";
        if (!name) return [];
        const signatureUrl =
          "signatureUrl" in row && row.signatureUrl ? String(row.signatureUrl) : undefined;
        return [{ name, signatureUrl }];
      })
    : [];

  return { isLoading, eSignatures };
}
