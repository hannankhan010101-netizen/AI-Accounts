"use client";

import { useTenantReferenceQuery } from "@/lib/api/tenant-query";
import { appSettingsApi, type PrintTemplateSettings } from "@/lib/api/tenant";

export function usePrintTemplate(code: string) {
  return useTenantReferenceQuery(
    ["print-template", code],
    () => appSettingsApi.getPrintTemplate(code),
    { enabled: Boolean(code) },
  );
}

export function resolvePrintTitle(
  fallback: string,
  template: Partial<PrintTemplateSettings> | undefined,
): string {
  const t = template?.title?.trim();
  return t || fallback;
}

export function resolvePrintPaperClass(template: Partial<PrintTemplateSettings> | undefined): string {
  return template?.paperSize === "Letter" ? "max-w-[216mm]" : "max-w-[210mm]";
}
