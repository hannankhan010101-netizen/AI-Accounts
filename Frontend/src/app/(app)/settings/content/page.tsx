/** Content Settings hub — catalog §12.14 (Forms / Menu / Listing) */
"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { invalidateTenantQueries, useTenantDetailQuery } from "@/lib/api/tenant-query";

import { ListingColumnEditor } from "@/components/settings/listing-column-editor";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { FORM_BRANCHES, formsForBranch } from "@/config/forms-catalog";
import { appSettingsApi, type ListingColumnSetting, type MenuItemSetting } from "@/lib/api/tenant";
import { defaultMenuItemsFromNav } from "@/lib/navigation/apply-menu-layout";
import { cn } from "@/lib/utils";

type ContentSection = "forms" | "menu" | "listing";

export default function ContentSettingsPage() {
  const qc = useQueryClient();
  const [section, setSection] = useState<ContentSection>("listing");
  const [formBranch, setFormBranch] = useState(FORM_BRANCHES[0] ?? "Sales Forms");
  const listingsQuery = useTenantDetailQuery(
    ["content-listings"],
    () => appSettingsApi.listContentListings(),
    { enabled: section === "listing" },
  );
  const listingCatalog = listingsQuery.data?.result ?? [];
  const listingBranches = useMemo(
    () => [...new Set(listingCatalog.map((l) => l.branch))],
    [listingCatalog],
  );
  const [listingBranch, setListingBranch] = useState("");
  const listingBranchItems = useMemo(
    () => listingCatalog.filter((l) => l.branch === listingBranch),
    [listingBranch, listingCatalog],
  );
  const formBranchItems = useMemo(() => formsForBranch(formBranch), [formBranch]);
  const [formId, setFormId] = useState(formBranchItems[0]?.id ?? "");
  const [listingId, setListingId] = useState(listingBranchItems[0]?.id ?? "");
  const [formDraft, setFormDraft] = useState<ListingColumnSetting[] | null>(null);
  const [listingDraft, setListingDraft] = useState<ListingColumnSetting[] | null>(null);
  const [menuDraft, setMenuDraft] = useState<MenuItemSetting[] | null>(null);

  useEffect(() => {
    setFormId(formBranchItems[0]?.id ?? "");
    setFormDraft(null);
  }, [formBranch, formBranchItems]);

  useEffect(() => {
    if (!listingBranch && listingBranches.length > 0) {
      setListingBranch(listingBranches[0] ?? "");
    }
  }, [listingBranch, listingBranches]);

  useEffect(() => {
    setListingId(listingBranchItems[0]?.id ?? "");
    setListingDraft(null);
  }, [listingBranch, listingBranchItems]);

  const formLayoutQuery = useTenantDetailQuery(
    ["form-layout", formId],
    () => appSettingsApi.getFormLayout(formId),
    { enabled: section === "forms" && Boolean(formId) },
  );

  const listingLayoutQuery = useTenantDetailQuery(
    ["listing-layout", listingId],
    () => appSettingsApi.getListingLayout(listingId),
    { enabled: section === "listing" && Boolean(listingId) },
  );

  const menuLayoutQuery = useTenantDetailQuery(
    ["content-menu"],
    () => appSettingsApi.getMenuLayout(),
    { enabled: section === "menu" },
  );

  useEffect(() => {
    if (formLayoutQuery.data?.result.fields) {
      setFormDraft(formLayoutQuery.data.result.fields);
    }
  }, [formLayoutQuery.data?.result.fields, formId]);

  useEffect(() => {
    if (listingLayoutQuery.data?.result.columns) {
      setListingDraft(listingLayoutQuery.data.result.columns);
    }
  }, [listingLayoutQuery.data?.result.columns, listingId]);

  useEffect(() => {
    if (menuLayoutQuery.data?.result.items) {
      setMenuDraft(menuLayoutQuery.data.result.items);
    }
  }, [menuLayoutQuery.data?.result.items]);

  const saveForm = useMutation({
    mutationFn: () => appSettingsApi.putFormLayout(formId, formDraft ?? []),
    onSuccess: () => void invalidateTenantQueries(qc, "form-layout", formId),
  });

  const saveListing = useMutation({
    mutationFn: () => appSettingsApi.putListingLayout(listingId, listingDraft ?? []),
    onSuccess: () => void invalidateTenantQueries(qc, "listing-layout", listingId),
  });

  const saveMenu = useMutation({
    mutationFn: () => appSettingsApi.putMenuLayout(menuDraft ?? []),
    onSuccess: () => void invalidateTenantQueries(qc, "content-menu"),
  });

  const activeFormLabel = formBranchItems.find((f) => f.id === formId)?.label ?? "Form";
  const activeListingLabel = listingBranchItems.find((l) => l.id === listingId)?.label ?? "Listing";

  return (
    <div>
      <PageHeader
        title="Content settings"
        breadcrumb="Settings / Content settings"
        description="Configure form fields, sidebar menu labels, and list column layouts in one place."
      />

      <div className="mb-4 flex flex-wrap gap-2">
        {(
          [
            ["forms", "Forms"],
            ["menu", "Menu"],
            ["listing", "Listing"],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            className={cn(
              "rounded-lg border px-4 py-2 text-sm font-medium",
              section === id
                ? "border-brand bg-brand/10 text-brand"
                : "border-border text-fg-muted hover:bg-surface",
            )}
            onClick={() => setSection(id)}
          >
            {label}
          </button>
        ))}
      </div>

      {section === "forms" ? (
        <div className="grid gap-6 lg:grid-cols-[240px_1fr]">
          <aside className="space-y-3 rounded-lg border border-border bg-surface p-4">
            {FORM_BRANCHES.map((b) => (
              <div key={b}>
                <button
                  type="button"
                  className={cn(
                    "mb-1 w-full rounded px-2 py-1 text-left text-sm font-medium",
                    formBranch === b ? "surface-brand-soft text-brand" : "text-fg hover:bg-canvas",
                  )}
                  onClick={() => setFormBranch(b)}
                >
                  {b}
                </button>
                {formBranch === b ? (
                  <ul className="ml-2 space-y-1 border-l border-border pl-2">
                    {formBranchItems.map((f) => (
                      <li key={f.id}>
                        <button
                          type="button"
                          className={cn(
                            "w-full rounded px-2 py-1 text-left text-sm",
                            formId === f.id
                              ? "bg-canvas font-medium text-fg"
                              : "text-fg-muted hover:bg-canvas hover:text-fg",
                          )}
                          onClick={() => {
                            setFormId(f.id);
                            setFormDraft(null);
                          }}
                        >
                          {f.label}
                        </button>
                      </li>
                    ))}
                  </ul>
                ) : null}
              </div>
            ))}
          </aside>
          <div>
            {formLayoutQuery.isLoading ? (
              <WorkspaceLoading />
            ) : formDraft && formId ? (
              <>
                <h2 className="mb-3 text-lg font-semibold text-fg">{activeFormLabel}</h2>
                <ListingColumnEditor
                  columns={formDraft}
                  onChange={setFormDraft}
                  onSave={() => saveForm.mutate()}
                  onReset={() => {
                    setFormDraft(null);
                    void formLayoutQuery.refetch();
                  }}
                  saving={saveForm.isPending}
                />
              </>
            ) : (
              <p className="text-sm text-fg-muted">Select a form to edit fields.</p>
            )}
          </div>
        </div>
      ) : null}

      {section === "menu" ? (
        <div>
          {menuLayoutQuery.isLoading ? (
            <WorkspaceLoading />
          ) : menuDraft ? (
            <>
              <h2 className="mb-3 text-lg font-semibold text-fg">Sidebar menu</h2>
              <ListingColumnEditor
                columns={menuDraft.map((m) => ({
                  key: m.href,
                  label: `${m.group} — ${m.label}`,
                  active: m.active,
                  order: m.order,
                }))}
                onChange={(rows) =>
                  setMenuDraft(
                    rows.map((r, i) => {
                      const prev = menuDraft.find((m) => m.href === r.key);
                      return {
                        href: r.key,
                        group: prev?.group ?? "",
                        label: r.label.includes(" — ")
                          ? r.label.split(" — ").slice(1).join(" — ")
                          : r.label,
                        active: r.active,
                        order: r.order ?? i,
                      };
                    }),
                  )
                }
                onSave={() => saveMenu.mutate()}
                onReset={() => {
                  setMenuDraft(defaultMenuItemsFromNav());
                }}
                saving={saveMenu.isPending}
              />
            </>
          ) : null}
        </div>
      ) : null}

      {section === "listing" ? (
        <div className="grid gap-6 lg:grid-cols-[240px_1fr]">
          <aside className="space-y-3 rounded-lg border border-border bg-surface p-4">
            {listingsQuery.isLoading ? (
              <WorkspaceLoading />
            ) : listingBranches.length === 0 ? (
              <p className="text-sm text-fg-muted">No listings available.</p>
            ) : (
              listingBranches.map((b) => (
                <div key={b}>
                  <button
                    type="button"
                    className={cn(
                      "mb-1 w-full rounded px-2 py-1 text-left text-sm font-medium",
                      listingBranch === b ? "surface-brand-soft text-brand" : "text-fg hover:bg-canvas",
                    )}
                    onClick={() => setListingBranch(b)}
                  >
                    {b}
                  </button>
                  {listingBranch === b ? (
                    <ul className="ml-2 space-y-1 border-l border-border pl-2">
                      {listingBranchItems.map((l) => (
                        <li key={l.id}>
                          <button
                            type="button"
                            className={cn(
                              "w-full rounded px-2 py-1 text-left text-sm",
                              listingId === l.id
                                ? "bg-canvas font-medium text-fg"
                                : "text-fg-muted hover:bg-canvas hover:text-fg",
                            )}
                            onClick={() => {
                              setListingId(l.id);
                              setListingDraft(null);
                            }}
                          >
                            {l.label}
                          </button>
                        </li>
                      ))}
                    </ul>
                  ) : null}
                </div>
              ))
            )}
          </aside>
          <div>
            {listingsQuery.isLoading || listingLayoutQuery.isLoading ? (
              <WorkspaceLoading />
            ) : listingDraft && listingId ? (
              <>
                <h2 className="mb-3 text-lg font-semibold text-fg">{activeListingLabel}</h2>
                <ListingColumnEditor
                  columns={listingDraft}
                  onChange={setListingDraft}
                  onSave={() => saveListing.mutate()}
                  onReset={() => {
                    setListingDraft(null);
                    void listingLayoutQuery.refetch();
                  }}
                  saving={saveListing.isPending}
                />
              </>
            ) : (
              <p className="text-sm text-fg-muted">Select a listing to edit columns.</p>
            )}
          </div>
        </div>
      ) : null}

      <p className="mt-6 text-xs text-fg-muted">
        Column and filter policies:{" "}
        <Link href="/settings/columns" className="text-brand hover:underline">
          Column management
        </Link>
        {" · "}
        <Link href="/settings/filters" className="text-brand hover:underline">
          Filters management
        </Link>
      </p>
    </div>
  );
}
