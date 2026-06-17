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
import { projectsApi, type ProjectRow } from "@/lib/api/tenant";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";

export default function ProjectsSettingsPage() {
  const qc = useQueryClient();
  const [code, setCode] = useState("");
  const [name, setName] = useState("");

  const { data, isLoading, error } = useTenantReferenceQuery(["projects"], () => projectsApi.list());

  const create = useMutation({
    mutationFn: () => projectsApi.create({ code, name }),
    onSuccess: () => {
      setCode("");
      setName("");
      void invalidateTenantQueries(qc, "projects");
    },
  });

  const toggleActive = useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) =>
      projectsApi.update(id, { isActive }),
    onSuccess: () => void invalidateTenantQueries(qc, "projects"),
  });

  const columns = responsiveListColumns<ProjectRow>([
    { key: "code", header: "Code", sortable: true, sortAccessor: (r) => r.code },
    { key: "name", header: "Name", sortable: true, sortAccessor: (r) => r.name },
    {
      key: "isActive",
      header: "Active",
      render: (r) => (
        <Checkbox
          checked={r.isActive}
          onChange={(e) => {
            e.stopPropagation();
            toggleActive.mutate({ id: r.id, isActive: !r.isActive });
          }}
        />
      ),
    },
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Projects"
        description="Project codes for job costing and document tagging (FA §2.6)."
      />
      <div className="flex max-w-md flex-wrap items-end gap-2">
        <div className="min-w-[8rem] flex-1">
          <FormField label="Code">
            <Input value={code} onChange={(e) => setCode(e.target.value)} />
          </FormField>
        </div>
        <div className="min-w-[8rem] flex-1">
          <FormField label="Name">
            <Input value={name} onChange={(e) => setName(e.target.value)} />
          </FormField>
        </div>
        <Button
          onClick={() => create.mutate()}
          disabled={create.isPending || !code || !name}
        >
          Add project
        </Button>
      </div>
      <EnterpriseGrid<ProjectRow>
        columns={columns}
        rows={data?.result ?? []}
        loading={isLoading}
        error={error}
        emptyMessage="No projects yet."
        getRowId={(r) => r.id}
      />
    </div>
  );
}
