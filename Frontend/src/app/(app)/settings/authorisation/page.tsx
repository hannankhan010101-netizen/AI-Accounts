"use client";
import { invalidateTenantQueries, useTenantReferenceQuery } from "@/lib/api/tenant-query";



import { useState } from "react";

import { useMutation, useQueryClient } from "@tanstack/react-query";



import { Button } from "@/components/ui/button";

import { EnterpriseGrid } from "@/components/ui/enterprise-grid";

import { FormField } from "@/components/ui/form-field";

import { Input } from "@/components/ui/input";

import { PageHeader } from "@/components/ui/page-header";

import { StatusBadge } from "@/components/app/status-badge";

import {

  approvalApi,

  type ApprovalPolicyRow,

  type ApprovalRequestRow,

} from "@/lib/api/tenant";



import { responsiveListColumns } from "@/lib/grid/responsive-columns";



const POLICY_ENTITY_TYPES = [

  { value: "sales_invoice", label: "Sales invoice" },

  { value: "supplier_bill", label: "Supplier bill" },

  { value: "sales_credit", label: "Sales credit" },

  { value: "supplier_credit", label: "Supplier credit" },

  { value: "journal", label: "Journal" },

];



function policyThreshold(row: ApprovalPolicyRow | undefined): string {

  if (!row?.rules) return "";

  const raw = row.rules.minAmount ?? row.rules.requiresApprovalAbove;

  return raw != null ? String(raw) : "";

}



export default function AuthorisationSettingsPage() {

  const qc = useQueryClient();

  const [entityType, setEntityType] = useState(POLICY_ENTITY_TYPES[0].value);

  const [minAmount, setMinAmount] = useState("");



  const policiesQuery = useTenantReferenceQuery(["approval-policies"], () => approvalApi.listPolicies());



  const requestsQuery = useTenantReferenceQuery(["approval-requests", "pending"], () => approvalApi.listRequests("pending"));



  const savePolicy = useMutation({

    mutationFn: () =>

      approvalApi.upsertPolicy({

        entityType,

        rules: { minAmount: Number(minAmount) || 0 },

      }),

    onSuccess: () => void invalidateTenantQueries(qc, "approval-policies"),

  });



  const approve = useMutation({

    mutationFn: (id: string) => approvalApi.approve(id),

    onSuccess: () => void invalidateTenantQueries(qc, "approval-requests"),

  });



  const reject = useMutation({

    mutationFn: (id: string) => approvalApi.reject(id),

    onSuccess: () => void invalidateTenantQueries(qc, "approval-requests"),

  });



  const policies = policiesQuery.data?.result ?? [];

  const selectedPolicy = policies.find((p) => p.entityType === entityType);



  const policyColumns = responsiveListColumns<ApprovalPolicyRow>([

    { key: "entityType", header: "Entity", sortable: true, sortAccessor: (r) => r.entityType },

    {

      key: "rules",

      header: "Min amount",

      render: (r) => policyThreshold(r) || "—",

    },

  ]);



  const requestColumns = responsiveListColumns<ApprovalRequestRow>([

    { key: "entityType", header: "Entity", sortable: true, sortAccessor: (r) => r.entityType },

    { key: "entityId", header: "Document id", render: (r) => r.entityId },

    {

      key: "amount",

      header: "Amount",

      align: "right",

      sortable: true,

      sortAccessor: (r) => Number(r.amount),

    },

    {

      key: "status",

      header: "Status",

      render: (r) => <StatusBadge status={r.status} />,

    },

    {

      key: "actions",

      header: "Actions",

      render: (r) => (

        <div className="flex gap-2">

          <Button

            type="button"

            size="sm"

            disabled={approve.isPending}

            onClick={(e) => {

              e.stopPropagation();

              approve.mutate(r.id);

            }}

          >

            Approve

          </Button>

          <Button

            type="button"

            size="sm"

            variant="outline"

            disabled={reject.isPending}

            onClick={(e) => {

              e.stopPropagation();

              reject.mutate(r.id);

            }}

          >

            Reject

          </Button>

        </div>

      ),

    },

  ]);



  return (

    <div className="space-y-8">

      <PageHeader

        title="Authorisation"

        description="Approval thresholds and pending requests before posting high-value documents."

      />



      <section className="space-y-4">

        <h2 className="text-sm font-semibold text-fg">Approval policies</h2>

        <div className="flex max-w-xl flex-wrap items-end gap-3">

          <FormField label="Entity type">

            <select

              className="h-9 w-full rounded-md border border-border bg-surface px-2 text-sm"

              value={entityType}

              onChange={(e) => {

                setEntityType(e.target.value);

                const p = policies.find((row) => row.entityType === e.target.value);

                setMinAmount(policyThreshold(p));

              }}

            >

              {POLICY_ENTITY_TYPES.map((t) => (

                <option key={t.value} value={t.value}>

                  {t.label}

                </option>

              ))}

            </select>

          </FormField>

          <FormField label="Requires approval above">

            <Input

              value={minAmount || policyThreshold(selectedPolicy)}

              onChange={(e) => setMinAmount(e.target.value)}

              placeholder="0 = disabled"

            />

          </FormField>

          <Button

            onClick={() => savePolicy.mutate()}

            disabled={savePolicy.isPending}

          >

            Save policy

          </Button>

        </div>

        <EnterpriseGrid<ApprovalPolicyRow>

          columns={policyColumns}

          rows={policies}

          loading={policiesQuery.isLoading}

          error={policiesQuery.error}

          emptyMessage="No policies configured."

          getRowId={(r) => r.id}

        />

      </section>



      <section className="space-y-4">

        <h2 className="text-sm font-semibold text-fg">Pending requests</h2>

        <EnterpriseGrid<ApprovalRequestRow>

          columns={requestColumns}

          rows={requestsQuery.data?.result ?? []}

          loading={requestsQuery.isLoading}

          error={requestsQuery.error}

          emptyMessage="No pending approval requests."

          getRowId={(r) => r.id}

        />

      </section>

    </div>

  );

}

