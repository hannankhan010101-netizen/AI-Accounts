"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useQuery } from "@tanstack/react-query";

import { settingsApi } from "@/lib/api/tenant";

export function useBusinessPrintHeader() {
  const { data, isLoading } = useTenantListQuery(["business-information"], () => settingsApi.getBusinessInformation());
  const business = data?.result;
  const businessAddress = business
    ? [
        business.addressLine1,
        business.addressLine2,
        business.addressLine3,
        business.addressLine4,
        business.addressLine5,
      ]
        .filter(Boolean)
        .join("\n")
    : null;

  return {
    isLoading,
    businessName: business?.businessName ?? null,
    businessAddress,
    businessLogoUrl: business?.logoUrl ?? null,
  };
}
