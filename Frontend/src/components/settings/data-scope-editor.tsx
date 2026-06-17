"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { useToast } from "@/components/ui/toast";
import { accessControlApi } from "@/lib/api/tenant";

export type DataScopeMember = {
  membershipId: string;
  label: string;
};

type ScopeFields = {
  customerIds: string[];
  supplierIds: string[];
  productIds: string[];
};

const EMPTY_SCOPE: ScopeFields = {
  customerIds: [],
  supplierIds: [],
  productIds: [],
};

function parseCsv(value: string): string[] {
  return value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

function toAssignments(scope: ScopeFields): { scopeType: string; scopeId: string }[] {
  const out: { scopeType: string; scopeId: string }[] = [];
  for (const id of scope.customerIds) out.push({ scopeType: "customer", scopeId: id });
  for (const id of scope.supplierIds) out.push({ scopeType: "supplier", scopeId: id });
  for (const id of scope.productIds) out.push({ scopeType: "product", scopeId: id });
  return out;
}

function fromAssignments(rows: { scopeType: string; scopeId: string }[]): ScopeFields {
  const scope = { ...EMPTY_SCOPE };
  for (const row of rows) {
    if (row.scopeType === "customer") scope.customerIds.push(row.scopeId);
    if (row.scopeType === "supplier") scope.supplierIds.push(row.scopeId);
    if (row.scopeType === "product") scope.productIds.push(row.scopeId);
  }
  return scope;
}

type DataScopeEditorProps = {
  members: DataScopeMember[];
  customerHint?: string;
  supplierHint?: string;
  productHint?: string;
  disabled?: boolean;
};

export function DataScopeEditor({
  members,
  customerHint,
  supplierHint,
  productHint,
  disabled,
}: DataScopeEditorProps) {
  const toast = useToast();
  const [membershipId, setMembershipId] = useState("");
  const [scope, setScope] = useState<ScopeFields>(EMPTY_SCOPE);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!membershipId) {
      setScope(EMPTY_SCOPE);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    void accessControlApi.listDataScope(membershipId).then(
      (res) => {
        if (cancelled) return;
        setScope(fromAssignments(res.result ?? []));
        setLoading(false);
      },
      (err: Error) => {
        if (cancelled) return;
        setError(err.message);
        setLoading(false);
      },
    );
    return () => {
      cancelled = true;
    };
  }, [membershipId]);

  async function save() {
    if (!membershipId) return;
    setSaving(true);
    setError(null);
    try {
      await accessControlApi.replaceDataScope(membershipId, toAssignments(scope));
      toast.success("Data scope saved.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <FormField label="User">
        <Select
          value={membershipId}
          disabled={disabled}
          onChange={(e) => setMembershipId(e.target.value)}
        >
          <option value="">Select user…</option>
          {members.map((m) => (
            <option key={m.membershipId} value={m.membershipId}>
              {m.label}
            </option>
          ))}
        </Select>
      </FormField>

      {!membershipId ? (
        <p className="text-sm text-fg-muted">Select a user to configure data scope.</p>
      ) : loading ? (
        <p className="text-sm text-fg-muted">Loading assignments…</p>
      ) : (
        <>
          <FormField label="Customers (comma-separated codes or IDs, * for all)">
            <Input
              disabled={disabled}
              value={scope.customerIds.join(", ")}
              placeholder={customerHint ?? "C001, C002"}
              onChange={(e) =>
                setScope((prev) => ({ ...prev, customerIds: parseCsv(e.target.value) }))
              }
            />
          </FormField>
          <FormField label="Suppliers (comma-separated codes or IDs, * for all)">
            <Input
              disabled={disabled}
              value={scope.supplierIds.join(", ")}
              placeholder={supplierHint ?? "S001"}
              onChange={(e) =>
                setScope((prev) => ({ ...prev, supplierIds: parseCsv(e.target.value) }))
              }
            />
          </FormField>
          <FormField label="Products (comma-separated codes or IDs, * for all)">
            <Input
              disabled={disabled}
              value={scope.productIds.join(", ")}
              placeholder={productHint ?? "P001"}
              onChange={(e) =>
                setScope((prev) => ({ ...prev, productIds: parseCsv(e.target.value) }))
              }
            />
          </FormField>
          {!disabled ? (
            <Button type="button" disabled={saving} onClick={() => void save()}>
              {saving ? "Saving…" : "Save data scope"}
            </Button>
          ) : null}
        </>
      )}

      {error ? <p className="text-sm text-status-danger">{error}</p> : null}
    </div>
  );
}
