"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { assemblyApi } from "@/lib/api/tenant";

export default function NewAssemblyJobPage() {
  const router = useRouter();
  const [templateId, setTemplateId] = useState("");
  const [jobDate, setJobDate] = useState(new Date().toISOString().slice(0, 10));
  const [quantity, setQuantity] = useState("1");
  const [batchNumber, setBatchNumber] = useState("");
  const [expiryDate, setExpiryDate] = useState("");

  const { data: templates } = useTenantListQuery(["assembly-templates"], () => assemblyApi.listTemplates());

  const save = useMutation({
    mutationFn: () =>
      assemblyApi.createJob({
        templateId,
        jobDate: new Date(jobDate).toISOString(),
        quantity,
        ...(batchNumber.trim() ? { batchNumber: batchNumber.trim() } : {}),
        ...(expiryDate ? { expiryDate: new Date(expiryDate).toISOString() } : {}),
      }),
    onSuccess: () => router.push("/inventory/assembly/jobs"),
  });

  return (
    <div className="mx-auto max-w-lg space-y-4">
      <PageHeader title="New assembly job" breadcrumb="Stock / Assembly / New job" />
      <FormField label="Template">
        <Select value={templateId} onChange={(e) => setTemplateId(e.target.value)}>
          <option value="">Select template</option>
          {(templates?.result ?? []).map((t) => (
            <option key={t.id} value={t.id}>
              {t.code} — {t.name}
            </option>
          ))}
        </Select>
      </FormField>
      <FormField label="Job date">
        <Input type="date" value={jobDate} onChange={(e) => setJobDate(e.target.value)} />
      </FormField>
      <FormField label="Quantity">
        <Input value={quantity} onChange={(e) => setQuantity(e.target.value)} />
      </FormField>
      <FormField label="Batch number (optional)">
        <Input value={batchNumber} onChange={(e) => setBatchNumber(e.target.value)} />
      </FormField>
      <FormField label="Expiry date (optional)">
        <Input type="date" value={expiryDate} onChange={(e) => setExpiryDate(e.target.value)} />
      </FormField>
      <div className="flex gap-2">
        <Button variant="outline" onClick={() => router.back()}>
          Cancel
        </Button>
        <Button
          onClick={() => save.mutate()}
          disabled={save.isPending || !templateId || !quantity}
        >
          Create job
        </Button>
      </div>
    </div>
  );
}
