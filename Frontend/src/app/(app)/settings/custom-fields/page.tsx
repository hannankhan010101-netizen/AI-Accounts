/** Custom field definitions — P11. */
"use client";
import { invalidateTenantQueries, useTenantReferenceQuery } from "@/lib/api/tenant-query";

import { useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { customFieldsApi } from "@/lib/api/tenant";
import { useClientList } from "@/lib/hooks/use-client-list";
import { matchText } from "@/lib/list/document-list-filters";


export interface CustomFieldDefinitionRow {
  id: string;
  entityType: string;
  fieldKey: string;
  label: string;
  fieldType: string;
  [key: string]: unknown;
}

export default function CustomFieldsPage() {
  const qc = useQueryClient();
  const [entityType, setEntityType] = useState("customer");
  const [fieldKey, setFieldKey] = useState("");
  const [label, setLabel] = useState("");
  const [fieldType, setFieldType] = useState("text");
  const [isRequired, setIsRequired] = useState(false);
  const [picklistText, setPicklistText] = useState("");

  const { data, isLoading, error } = useTenantReferenceQuery(["custom-field-definitions"], () => customFieldsApi.listDefinitions());

  const rows = (data?.result ?? []) as CustomFieldDefinitionRow[];

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.entityType, r.fieldKey, r.label, r.fieldType], q),
  });

  const create = useMutation({
    mutationFn: () =>
      customFieldsApi.createDefinition({
        entityType,
        fieldKey,
        label: label || fieldKey,
        fieldType,
        isRequired,
        picklistOptions:
          fieldType === "picklist"
            ? picklistText.split(",").map((s) => s.trim()).filter(Boolean)
            : undefined,
      }),
    onSuccess: () => {
      setFieldKey("");
      setLabel("");
      setPicklistText("");
      void invalidateTenantQueries(qc, "custom-field-definitions");
    },
  });

  const columns = useMemo(
    () => responsiveListColumns<CustomFieldDefinitionRow>([
      {
        key: "entityType",
        header: "Entity",
        sortable: true,
        sortAccessor: (r) => r.entityType,
        render: (r) => <span className="capitalize">{r.entityType}</span>,
      },
      {
        key: "fieldKey",
        header: "Key",
        sortable: true,
        sortAccessor: (r) => r.fieldKey,
        render: (r) => <span className="font-mono text-xs">{r.fieldKey}</span>,
      },
      { key: "label", header: "Label", sortable: true, sortAccessor: (r) => r.label },
      { key: "fieldType", header: "Type", sortable: true, sortAccessor: (r) => r.fieldType },
    ]),
    [],
  );

  return (
    <div>
      <PageHeader
        title="Custom fields"
        breadcrumb="Admin / Custom fields"
        description="Define keys used on customers and products; report 185 can group by customFields.{key}."
      />

      <section className="mb-6 max-w-lg rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold text-fg">Add definition</h2>
        <div className="mt-3 grid gap-3">
          <FormField label="Entity type">
            <Select value={entityType} onChange={(e) => setEntityType(e.target.value)}>
              <option value="customer">Customer</option>
              <option value="product">Product</option>
            </Select>
          </FormField>
          <FormField label="Field key">
            <Input
              placeholder="e.g. region"
              value={fieldKey}
              onChange={(e) => setFieldKey(e.target.value)}
            />
          </FormField>
          <FormField label="Field type">
            <Select value={fieldType} onChange={(e) => setFieldType(e.target.value)}>
              <option value="text">Text</option>
              <option value="number">Number</option>
              <option value="date">Date</option>
              <option value="picklist">Picklist</option>
            </Select>
          </FormField>
          <FormField label="Label">
            <Input placeholder="Display label" value={label} onChange={(e) => setLabel(e.target.value)} />
          </FormField>
          <label className="flex items-center gap-2 text-sm">
            <Checkbox checked={isRequired} onChange={(e) => setIsRequired(e.target.checked)} />
            Required
          </label>
          {fieldType === "picklist" ? (
            <FormField label="Picklist options">
              <Input
                placeholder="Comma-separated"
                value={picklistText}
                onChange={(e) => setPicklistText(e.target.value)}
              />
            </FormField>
          ) : null}
          <Button
            type="button"
            disabled={!fieldKey || create.isPending}
            onClick={() => create.mutate()}
          >
            {create.isPending ? "Adding…" : "Add field"}
          </Button>
        </div>
      </section>

      <h2 className="mb-2 text-sm font-semibold text-fg">Definitions</h2>
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<CustomFieldDefinitionRow>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        emptyMessage="No custom fields yet."
        pagination={pagination}
        exportCsv={{ ...buildGridExport("custom-fields", columns), rows: filtered }}
        getRowId={(r) => r.id}
      />
    </div>
  );
}
