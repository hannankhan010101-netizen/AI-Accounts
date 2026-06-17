"use client";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";



import { appSettingsApi } from "@/lib/api/tenant";
import {
  DEFAULT_OP_METHOD_IDS,
  OP_METHOD_CATALOG,
  type OpMethodDef,
} from "@/lib/settings/op-methods-catalog";


type OpMethodsSettings = {
  defaultPaymentMethod?: string;
  enabledMethods?: string[];
};

export function useOpMethods(): {
  methods: OpMethodDef[];
  defaultMethod: string;
  isLoading: boolean;
} {
  const { data, isLoading } = useTenantReferenceQuery(["op-methods-settings"], () => appSettingsApi.getOpMethodsSettings());

  const raw = data?.result as OpMethodsSettings | undefined;
  const enabledIds = Array.isArray(raw?.enabledMethods)
    ? raw!.enabledMethods.map(String)
    : [...DEFAULT_OP_METHOD_IDS];
  const enabled = new Set(enabledIds.length ? enabledIds : DEFAULT_OP_METHOD_IDS);
  const methods = OP_METHOD_CATALOG.filter((m) => enabled.has(m.id));
  const defaultMethod =
    raw?.defaultPaymentMethod && enabled.has(String(raw.defaultPaymentMethod))
      ? String(raw.defaultPaymentMethod)
      : methods[0]?.id ?? "cash";

  return { methods, defaultMethod, isLoading };
}
