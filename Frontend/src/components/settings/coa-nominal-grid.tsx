"use client";

import { useMemo } from "react";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { flattenCoaNominals, type FlatNominalRow } from "@/lib/coa/flatten-nominals";
import { useClientList } from "@/lib/hooks/use-client-list";
import { matchText } from "@/lib/list/document-list-filters";
import type { CoaTreeCategory } from "@/lib/api/tenant";

interface CoaNominalGridProps {
  categories: CoaTreeCategory[];
  loading?: boolean;
  error?: unknown;
  sections?: { id: string; label: string }[];
  onEdit?: (row: FlatNominalRow) => void;
  selectedIds?: Set<string>;
  onToggleSelect?: (id: string, checked: boolean) => void;
}

export function CoaNominalGrid({
  categories,
  loading,
  error,
  onEdit,
  selectedIds,
  onToggleSelect,
}: CoaNominalGridProps) {
  const rows = useMemo(() => flattenCoaNominals(categories), [categories]);

  const { search, setSearch, pageRows, pagination } = useClientList({
    rows,
    filterFn: (r, q) =>
      matchText(
        [r.code, r.name, r.description, r.categoryName, r.categoryType, r.sectionName, r.sectionCode],
        q,
      ),
  });

  const columns = useMemo(
    () => responsiveListColumns<FlatNominalRow>([
      ...(onToggleSelect
        ? [
            {
              key: "select",
              header: "",
              render: (r: FlatNominalRow) => (
                <Checkbox
                  checked={selectedIds?.has(r.id) ?? false}
                  aria-label={`Select ${r.code}`}
                  onChange={(e) => onToggleSelect(r.id, e.target.checked)}
                />
              ),
            } satisfies GridColumn<FlatNominalRow>,
          ]
        : []),
      {
        key: "code",
        header: "Code",
        sortable: true,
        sortAccessor: (r) => r.code,
        render: (r) => <span className="font-mono text-fg-muted">{r.code}</span>,
      },
      { key: "name", header: "Nominal", sortable: true, sortAccessor: (r) => r.name },
      {
        key: "categoryName",
        header: "Category",
        sortable: true,
        sortAccessor: (r) => r.categoryName,
      },
      {
        key: "categoryType",
        header: "Type",
        sortable: true,
        sortAccessor: (r) => r.categoryType,
      },
      {
        key: "sectionName",
        header: "Section",
        sortable: true,
        sortAccessor: (r) => r.sectionName,
        render: (r) => (
          <span>
            {r.sectionName}{" "}
            <span className="text-fg-muted">({r.sectionCode})</span>
          </span>
        ),
      },
      {
        key: "isChargeDeduction",
        header: "Deduction",
        render: (r) => (r.isChargeDeduction ? "Yes" : "—"),
      },
      ...(onEdit
        ? [
            {
              key: "actions",
              header: "",
              render: (r: FlatNominalRow) => (
                <Button type="button" size="sm" variant="outline" onClick={() => onEdit(r)}>
                  Edit
                </Button>
              ),
            } satisfies GridColumn<FlatNominalRow>,
          ]
        : []),
    ]),
    [onEdit, onToggleSelect, selectedIds],
  );

  return (
    <>
      <ListToolbar
        search={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search nominals by code, name, category…"
      />
      <EnterpriseGrid<FlatNominalRow>
        columns={columns}
        rows={pageRows}
        loading={loading}
        error={error}
        emptyMessage="No nominal accounts yet. Add sections and nominals from the tree view or Section Management."
        pagination={pagination}
        getRowId={(r) => r.id}
      />
    </>
  );
}
