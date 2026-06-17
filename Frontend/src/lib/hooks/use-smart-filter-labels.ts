"use client";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";



import { settingsApi } from "@/lib/api/tenant";


export type SmartModule = "sales" | "purchases" | "bank" | "fixedAssets";

export interface SmartFilterLabels {
  filter1: string;
  filter2: string;
  filter3: string;
  filter4: string;
  doc1: string;
  doc2: string;
  doc3: string;
  doc4: string;
}

const DEFAULT_LABELS: SmartFilterLabels = {
  filter1: "Filter 1",
  filter2: "Filter 2",
  filter3: "Filter 3",
  filter4: "Filter 4",
  doc1: "Doc 1",
  doc2: "Doc 2",
  doc3: "Doc 3",
  doc4: "Doc 4",
};

export function useSmartFilterLabels(module: SmartModule) {
  const { data, isLoading } = useTenantReferenceQuery(["smart-settings"], () => settingsApi.getSmartSettings());

  const payload = data?.result?.payload as Record<string, unknown> | undefined;
  const moduleBlock = payload?.[module] as
    | {
        smartFilters?: Record<string, string>;
        smartDocs?: Record<string, string>;
      }
    | undefined;

  const filters = moduleBlock?.smartFilters ?? {};
  const docs = moduleBlock?.smartDocs ?? {};

  const labels: SmartFilterLabels = {
    filter1: filters.filter1?.trim() || DEFAULT_LABELS.filter1,
    filter2: filters.filter2?.trim() || DEFAULT_LABELS.filter2,
    filter3: filters.filter3?.trim() || DEFAULT_LABELS.filter3,
    filter4: filters.filter4?.trim() || DEFAULT_LABELS.filter4,
    doc1: docs.doc1?.trim() || DEFAULT_LABELS.doc1,
    doc2: docs.doc2?.trim() || DEFAULT_LABELS.doc2,
    doc3: docs.doc3?.trim() || DEFAULT_LABELS.doc3,
    doc4: docs.doc4?.trim() || DEFAULT_LABELS.doc4,
  };

  return { labels, isLoading, hasCustomLabels: Boolean(moduleBlock) };
}
