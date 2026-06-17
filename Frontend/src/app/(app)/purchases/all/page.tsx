/** Purchases All — unified bills, payments, and credits (FastAccounts Purchases All). */

"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";




import Link from "next/link";

import { useRouter } from "next/navigation";

import { useMemo, useState } from "react";

import { useQuery } from "@tanstack/react-query";



import { ActivityListFilters, type ActivityFilterState } from "@/components/patterns/activity-list-filters";

import { Checkbox } from "@/components/ui/checkbox";

import { EnterpriseGrid } from "@/components/ui/enterprise-grid";

import { buildGridExport } from "@/lib/export/grid-export";

import { ListToolbar } from "@/components/ui/list-toolbar";

import { PageHeader } from "@/components/ui/page-header";

import { useClientList } from "@/lib/hooks/use-client-list";

import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";

import { useSupplierNameMap } from "@/lib/hooks/use-party-name-map";

import { responsiveListColumns } from "@/lib/grid/responsive-columns";

import { matchText } from "@/lib/list/document-list-filters";

import { activityApi, partiesApi, type ActivityRow } from "@/lib/api/tenant";

import { activityDetailHref } from "@/lib/activity/activity-links";



export default function PurchasesAllPage() {

  const router = useRouter();

  const supplierNameById = useSupplierNameMap();

  const [filters, setFilters] = useState<ActivityFilterState>({});



  const suppliersQuery = useTenantListQuery(["suppliers"], () => partiesApi.listSuppliers());



  const { data, isLoading, error } = useTenantListQuery(
    ["purchases-activity", filters],
    () => activityApi.listPurchases(filters),
  );



  const partyOptions = useMemo(

    () =>

      (suppliersQuery.data?.result ?? []).map((s) => ({

        id: s.id,

        label: s.code ? `${s.name} (${s.code})` : s.name,

      })),

    [suppliersQuery.data],

  );



  const statusOptions = useMemo(

    () =>

      Array.from(new Set((data?.result ?? []).map((r) => r.status ?? "").filter(Boolean))).sort(),

    [data?.result],

  );



  const { search, setSearch, pageRows, pagination, filtered } = useClientList({

    rows: data?.result,

    syncUrl: true,

    filterFn: (r, q) =>

      matchText(

        [r.docType, r.documentNumber, supplierNameById.get(r.partyId), r.partyId, r.status],

        q,

      ),

  });



  const baseColumns = useMemo(

    () =>

      responsiveListColumns<ActivityRow>([

        {

          key: "docType",

          header: "Type",

          sortable: true,

          sortAccessor: (r) => r.docType,

        },

        {

          key: "documentNumber",

          header: "Doc no.",

          sortable: true,

          sortAccessor: (r) => r.documentNumber,

          render: (r) => (

            <Link href={activityDetailHref(r)} className="font-mono text-brand hover:underline">

              {r.documentNumber}

            </Link>

          ),

        },

        {

          key: "documentDate",

          header: "Date",

          sortable: true,

          sortAccessor: (r) => r.documentDate,

          render: (r) => new Date(r.documentDate).toLocaleDateString(),

        },

        {

          key: "partyId",

          header: "Supplier",

          sortable: true,

          sortAccessor: (r) => supplierNameById.get(r.partyId) ?? r.partyId,

          render: (r) => supplierNameById.get(r.partyId) ?? r.partyId,

        },

        {

          key: "totalAmount",

          header: "Amount",

          align: "right",

          sortable: true,

          sortAccessor: (r) => Number(r.totalAmount),

        },

        {

          key: "status",

          header: "Status",

          sortable: true,

          sortAccessor: (r) => r.status ?? "",

        },

      ]),

    [supplierNameById],

  );

  const columns = useConfiguredListColumns("purchases-all", baseColumns);



  return (

    <div>

      <PageHeader
        title="All purchase activity"

        breadcrumb="Buy / All purchase activity"

        description="Bills, payments, and credits in one list — matches FastAccounts Purchases All."

      />



      <label className="mb-3 flex items-center gap-2 text-sm text-fg">

        <Checkbox

          checked={!!filters.includePlanning}

          onChange={(e) => setFilters((f) => ({ ...f, includePlanning: e.target.checked }))}

        />

        Include purchase orders, PDC issued, and GRN

      </label>



      <ActivityListFilters

        kind="purchases"

        value={filters}

        onChange={setFilters}

        partyOptions={partyOptions}

        statusOptions={statusOptions}

      />



      <ListToolbar

        search={search}

        onSearchChange={setSearch}

        searchPlaceholder="Search type, doc no., supplier…"

      />



      <EnterpriseGrid<ActivityRow>

        columns={columns}

        rows={pageRows}

        loading={isLoading}

        error={error}

        listEntity="purchase-activity"
        isSearching={Boolean(search)}

        onRowClick={(r) => router.push(activityDetailHref(r))}

        pagination={pagination}

        exportCsv={{ ...buildGridExport("purchases-all", columns), rows: filtered }}

      />

    </div>

  );

}

