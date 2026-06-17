"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { invalidateTenantQueries, useTenantReferenceQuery } from "@/lib/api/tenant-query";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { locationsApi, type LocationRow } from "@/lib/api/tenant";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";

export default function LocationsSettingsPage() {
  const qc = useQueryClient();
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [isMain, setIsMain] = useState(false);

  const { data, isLoading, error } = useTenantReferenceQuery(["locations"], () => locationsApi.list());

  const create = useMutation({
    mutationFn: () => locationsApi.create({ code, name, isMain }),
    onSuccess: () => {
      setCode("");
      setName("");
      setIsMain(false);
      void invalidateTenantQueries(qc, "locations");
    },
  });

  const setMain = useMutation({
    mutationFn: (id: string) => locationsApi.update(id, { isMain: true }),
    onSuccess: () => void invalidateTenantQueries(qc, "locations"),
  });

  const columns = responsiveListColumns<LocationRow>([
    { key: "code", header: "Code", sortable: true, sortAccessor: (r) => r.code },
    { key: "name", header: "Name", sortable: true, sortAccessor: (r) => r.name },
    {
      key: "isMain",
      header: "Main",
      render: (r) =>
        r.isMain ? (
          <span className="text-sm text-fg-muted">Main</span>
        ) : (
          <Button size="sm" variant="outline" onClick={() => setMain.mutate(r.id)}>
            Set main
          </Button>
        ),
    },
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Locations"
        description="Stock locations and multi-location setup (FA §12.7)."
      />
      <div className="max-w-md space-y-3">
        <FormField label="Code">
          <Input value={code} onChange={(e) => setCode(e.target.value)} />
        </FormField>
        <FormField label="Name">
          <Input value={name} onChange={(e) => setName(e.target.value)} />
        </FormField>
        <label className="flex items-center gap-2 text-sm">
          <Checkbox
            checked={isMain}
            onChange={(e) => setIsMain(e.target.checked)}
          />
          Main location
        </label>
        <Button
          onClick={() => create.mutate()}
          disabled={create.isPending || !code || !name}
        >
          Add location
        </Button>
      </div>
      <EnterpriseGrid<LocationRow>
        columns={columns}
        rows={data?.result ?? []}
        loading={isLoading}
        error={error}
        emptyMessage="No locations yet."
        getRowId={(r) => r.id}
      />
    </div>
  );
}
