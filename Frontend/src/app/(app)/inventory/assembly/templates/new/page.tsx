"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { assemblyApi } from "@/lib/api/tenant";

type LineRow = { componentProductCode: string; quantity: string };

export default function NewAssemblyTemplatePage() {
  const router = useRouter();
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [finishedProductCode, setFinishedProductCode] = useState("");
  const [lines, setLines] = useState<LineRow[]>([
    { componentProductCode: "", quantity: "1" },
  ]);

  const save = useMutation({
    mutationFn: () =>
      assemblyApi.createTemplate({
        code,
        name,
        finishedProductCode,
        lines: lines.filter((l) => l.componentProductCode.trim()),
      }),
    onSuccess: () => router.push("/inventory/assembly/templates"),
  });

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <PageHeader title="New assembly template" breadcrumb="Stock / Assembly / New template" />
      <FormField label="Code">
        <Input value={code} onChange={(e) => setCode(e.target.value)} />
      </FormField>
      <FormField label="Name">
        <Input value={name} onChange={(e) => setName(e.target.value)} />
      </FormField>
      <FormField label="Finished product code">
        <Input
          value={finishedProductCode}
          onChange={(e) => setFinishedProductCode(e.target.value)}
        />
      </FormField>
      <div className="space-y-2">
        <p className="text-sm font-medium">Components</p>
        {lines.map((line, i) => (
          <div key={i} className="flex gap-2">
            <Input
              placeholder="Product code"
              value={line.componentProductCode}
              onChange={(e) => {
                const next = [...lines];
                next[i] = { ...line, componentProductCode: e.target.value };
                setLines(next);
              }}
            />
            <Input
              placeholder="Qty"
              className="w-24"
              value={line.quantity}
              onChange={(e) => {
                const next = [...lines];
                next[i] = { ...line, quantity: e.target.value };
                setLines(next);
              }}
            />
          </div>
        ))}
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => setLines([...lines, { componentProductCode: "", quantity: "1" }])}
        >
          Add line
        </Button>
      </div>
      <div className="flex gap-2">
        <Button variant="outline" onClick={() => router.back()}>
          Cancel
        </Button>
        <Button
          onClick={() => save.mutate()}
          disabled={save.isPending || !code || !name || !finishedProductCode}
        >
          Save template
        </Button>
      </div>
    </div>
  );
}
