"use client";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";

import { useMemo } from "react";


import { appSettingsApi } from "@/lib/api/tenant";


/** Whether a form field is visible per Content Settings → Forms branch. */
export function useFormFieldVisibility(formId: string) {
  const { data } = useTenantReferenceQuery(["form-layout", formId], () => appSettingsApi.getFormLayout(formId));

  const activeKeys = useMemo(() => {
    const fields = data?.result.fields ?? [];
    return new Set(fields.filter((f) => f.active).map((f) => f.key));
  }, [data?.result.fields]);

  const isVisible = (key: string) => {
    if (!data?.result.fields?.length) return true;
    return activeKeys.has(key);
  };

  return { isVisible, fields: data?.result.fields ?? [] };
}
