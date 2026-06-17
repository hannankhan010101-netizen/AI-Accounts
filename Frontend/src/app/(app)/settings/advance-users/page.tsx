"use client";

import { useMemo } from "react";

import { DataScopeEditor } from "@/components/settings/data-scope-editor";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { inventoryApi, partiesApi, rbacApi } from "@/lib/api/tenant";
import { useTenantListQuery, useTenantReferenceQuery } from "@/lib/api/tenant-query";
import { usePermission } from "@/lib/rbac/can";
import { PERM_ACCESS_CONTROL_MANAGE } from "@/lib/rbac/permissions";

function memberLabel(row: {
  firstName?: string | null;
  lastName?: string | null;
  email?: string | null;
}): string {
  const name = `${row.firstName ?? ""} ${row.lastName ?? ""}`.trim();
  return name || row.email || "User";
}

export default function AdvanceUsersPage() {
  const canManage = usePermission(PERM_ACCESS_CONTROL_MANAGE);
  const usersQuery = useTenantListQuery(["rbac-users-ref"], () =>
    rbacApi.listUsers({ page: 1, pageSize: 200 }),
  );
  const customersQuery = useTenantReferenceQuery(["customers-ref"], () => partiesApi.listCustomers());
  const suppliersQuery = useTenantReferenceQuery(["suppliers-ref"], () => partiesApi.listSuppliers());
  const productsQuery = useTenantReferenceQuery(["products-ref"], () => inventoryApi.listProducts());

  const members = useMemo(
    () =>
      (usersQuery.data?.result?.items ?? []).map((row) => ({
        membershipId: String(row.id),
        label: memberLabel(row),
      })),
    [usersQuery.data?.result?.items],
  );

  const loading =
    usersQuery.isLoading ||
    customersQuery.isLoading ||
    suppliersQuery.isLoading ||
    productsQuery.isLoading;

  const customers = customersQuery.data?.result ?? [];
  const suppliers = suppliersQuery.data?.result ?? [];
  const products = productsQuery.data?.result ?? [];

  return (
    <div>
      <PageHeader
        title="Data scope"
        breadcrumb="Settings / Data scope"
        description="Limit which customers, suppliers, and products each user can see in sales and purchases."
      />

      {loading ? <WorkspaceLoading className="mt-4" /> : null}

      <section className="mt-4">
        <DataScopeEditor
          members={members}
          disabled={!canManage}
          customerHint={customers.slice(0, 3).map((c) => c.code).join(", ") || undefined}
          supplierHint={suppliers.slice(0, 3).map((s) => s.code).join(", ") || undefined}
          productHint={products.slice(0, 3).map((p) => p.code).join(", ") || undefined}
        />
      </section>
    </div>
  );
}
