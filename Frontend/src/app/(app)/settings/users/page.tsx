/** Users management — catalog §12.3.1 */
"use client";
import { useTenantReferenceQuery, useTenantListQuery, useTenantDetailQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { ActionMenu, ResponsiveActionCluster } from "@/components/ui/action-menu";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { useToast } from "@/components/ui/toast";
import { MultiRoleSelect } from "@/components/settings/multi-role-select";
import { RoleSelectField } from "@/components/settings/role-select-field";
import { UserInviteForm } from "@/components/settings/user-invite-form";
import { UserRowActions } from "@/components/settings/user-row-actions";
import {
  hasPermission,
  PERM_ROLES_MANAGE,
  PERM_USERS_INVITE,
} from "@/lib/rbac/permissions";
import { useUrlServerList } from "@/lib/hooks/use-url-server-list";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { rbacApi, billingApi, type RbacUser } from "@/lib/api/tenant";
import {
  brandLinkClasses,
  brandRowHighlightClasses,
  brandSoftClasses,
  warningSurfaceClasses,
} from "@/lib/design-tokens/brand-surfaces";
import { cn } from "@/lib/utils";

function memberUserId(row: RbacUser): string {
  return String(row.userId ?? row.id);
}

function memberRoleIds(row: RbacUser): string[] {
  const ids = row.roleIds;
  if (Array.isArray(ids) && ids.length > 0) {
    return ids.map(String);
  }
  const single = String(row.roleId ?? "");
  return single ? [single] : [];
}

function memberRoleId(row: RbacUser): string {
  return memberRoleIds(row)[0] ?? "";
}

function memberDisplayName(row: RbacUser): string {
  return `${row.firstName ?? ""} ${row.lastName ?? ""}`.trim() || "—";
}

function UserStatusBadge({
  active,
  emailVerified,
}: {
  active: boolean;
  emailVerified?: boolean;
}) {
  if (active && emailVerified === false) {
    return <Badge variant="warning">Pending OTP</Badge>;
  }
  return (
    <Badge variant={active ? "success" : "danger"}>
      {active ? "Active" : "Inactive"}
    </Badge>
  );
}

export default function UsersPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const highlightUserId = searchParams.get("userId")?.trim() || "";
  const reinviteUserIdParam = searchParams.get("reinviteUserId")?.trim() || "";
  const reinviteEmailParam = searchParams.get("reinviteEmail")?.trim() || "";
  const queryClient = useQueryClient();
  const toast = useToast();
  const {
    page,
    pageSize,
    search,
    setSearch,
    setPage,
    statusFilter,
    setStatusFilter,
  } = useUrlServerList(25);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [showInvite, setShowInvite] = useState(false);
  const [bulkRoleId, setBulkRoleId] = useState("");
  const [actionError, setActionError] = useState<string | null>(null);
  const [showReinvite, setShowReinvite] = useState(false);
  const [reinvite, setReinvite] = useState({ email: "", roleId: "" });

  const { data: permsData } = useTenantReferenceQuery(["my-permissions"], () => rbacApi.getMyPermissions());
  const myPerms = permsData?.result?.permissions ?? [];
  const canInvite = hasPermission(myPerms, PERM_USERS_INVITE);
  const canManageRoles = hasPermission(myPerms, PERM_ROLES_MANAGE);
  const canSelectRows = canManageRoles || canInvite;

  const { data: billingData } = useTenantReferenceQuery(["billing-status"], () => billingApi.status(), { enabled: canInvite });
  const seats = billingData?.result?.seats;
  const seatsAtLimit = seats?.atLimit === true;

  const { data: reinvitePrefill } = useTenantDetailQuery(
    ["rbac-user-reinvite", reinviteUserIdParam],
    () => rbacApi.listUsers({ userId: reinviteUserIdParam, page: 1, pageSize: 1 }),
    { enabled: Boolean(reinviteUserIdParam && canInvite) },
  );

  useEffect(() => {
    if (reinviteUserIdParam) setShowReinvite(true);
  }, [reinviteUserIdParam]);

  useEffect(() => {
    const row = reinvitePrefill?.result?.items?.[0];
    if (row?.email) {
      setReinvite((s) => ({ ...s, email: String(row.email) }));
    }
  }, [reinvitePrefill]);

  useEffect(() => {
    if (reinviteEmailParam) {
      setReinvite((s) => ({ ...s, email: reinviteEmailParam }));
      setShowReinvite(true);
    }
  }, [reinviteEmailParam]);

  useEffect(() => {
    setSelected(new Set());
  }, [page, pageSize, search, statusFilter, highlightUserId]);

  const lookupEmail = useMutation({
    mutationFn: (email: string) => rbacApi.lookupUserByEmail(email),
    onSuccess: (res) => {
      setReinvite((s) => ({ ...s, email: res.result.email }));
      setActionError(null);
    },
    onError: (e: Error) => setActionError(e.message),
  });

  const { data, isLoading, isFetching, error } = useTenantListQuery(
    ["rbac-users", page, search, statusFilter, highlightUserId],
    () =>
      rbacApi.listUsers({
        page,
        pageSize,
        q: highlightUserId ? undefined : search.trim() || undefined,
        userId: highlightUserId || undefined,
        isActive:
          statusFilter === "active" ? true : statusFilter === "inactive" ? false : undefined,
      }),
  );

  const { data: rolesData } = useTenantReferenceQuery(["rbac-roles"], () => rbacApi.listRoles(), { enabled: canManageRoles || canInvite });

  const roles = rolesData?.result ?? [];
  const rows = data?.result?.items ?? [];
  const total = data?.result?.total ?? 0;

  const invalidate = () => {
    void invalidateTenantQueries(queryClient, "rbac-users");
  };

  const pageUserIds = useMemo(
    () => rows.map((row) => memberUserId(row)),
    [rows],
  );
  const allPageSelected =
    pageUserIds.length > 0 && pageUserIds.every((id) => selected.has(id));
  const somePageSelected =
    pageUserIds.some((id) => selected.has(id)) && !allPageSelected;

  const toggleRow = useCallback((uid: string, checked: boolean) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (checked) next.add(uid);
      else next.delete(uid);
      return next;
    });
  }, []);

  const togglePageSelection = useCallback(
    (checked: boolean) => {
      setSelected((prev) => {
        const next = new Set(prev);
        for (const id of pageUserIds) {
          if (checked) next.add(id);
          else next.delete(id);
        }
        return next;
      });
    },
    [pageUserIds],
  );

  const reinviteMutation = useMutation({
    mutationFn: () =>
      rbacApi.reinviteByEmail({
        email: reinvite.email.trim(),
        roleId: reinvite.roleId,
      }),
    onSuccess: (res) => {
      setActionError(null);
      setShowReinvite(false);
      setReinvite({ email: "", roleId: "" });
      const sent = res.result.inviteEmailSent;
      toast.success(
        sent
          ? "User re-added to the company; invite email sent when applicable."
          : "User re-added; email was not sent (check SMTP settings).",
      );
      invalidate();
    },
    onError: (e: Error) => setActionError(e.message),
  });

  const bulkAssign = useMutation({
    mutationFn: () =>
      rbacApi.bulkAssignRole(Array.from(selected), bulkRoleId),
    onSuccess: () => {
      setSelected(new Set());
      setActionError(null);
      invalidate();
    },
    onError: (e: Error) => setActionError(e.message),
  });

  const bulkRevoke = useMutation({
    mutationFn: () => rbacApi.bulkRevokeMembership(Array.from(selected)),
    onSuccess: () => {
      setSelected(new Set());
      setActionError(null);
      invalidate();
    },
    onError: (e: Error) => setActionError(e.message),
  });

  const columns = useMemo(
    () =>
      responsiveListColumns<RbacUser>(
        [
          ...(canSelectRows
            ? [
                {
                  key: "select",
                  header: "Select",
                  headerNode: (
                    <Checkbox
                      aria-label="Select all users on this page"
                      checked={allPageSelected}
                      ref={(el: HTMLInputElement | null) => {
                        if (el) el.indeterminate = somePageSelected;
                      }}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                        togglePageSelection(e.target.checked)
                      }
                    />
                  ),
                  cardHidden: true,
                  sortable: false,
                  className: "w-10",
                  render: (r: RbacUser) => {
                    const uid = memberUserId(r);
                    return (
                      <Checkbox
                        aria-label={`Select ${memberDisplayName(r)}`}
                        checked={selected.has(uid)}
                        onChange={(e) => toggleRow(uid, e.target.checked)}
                      />
                    );
                  },
                } as GridColumn<RbacUser>,
              ]
            : []),
          {
            key: "name",
            header: "Name",
            sortable: true,
            sortAccessor: (r) => memberDisplayName(r),
            render: (r) => (
              <div className="min-w-0">
                <div className="font-medium text-fg">{memberDisplayName(r)}</div>
                <div className="truncate text-xs text-fg-muted md:hidden">
                  {r.email ?? "—"}
                </div>
              </div>
            ),
          },
          {
            key: "email",
            header: "Email",
            sortable: true,
            sortAccessor: (r) => String(r.email ?? ""),
            render: (r) => (
              <span className="block max-w-[16rem] truncate" title={String(r.email ?? "")}>
                {r.email ?? "—"}
              </span>
            ),
          },
          {
            key: "role",
            header: "Role",
            sortable: true,
            sortAccessor: (r) => String(r.roleName ?? r.role ?? ""),
            render: (r) => {
              const uid = memberUserId(r);
              if (!canManageRoles) {
                const names = memberRoleIds(r)
                  .map((id) => roles.find((role) => role.id === id)?.name ?? id)
                  .filter(Boolean);
                return names.length ? names.join(", ") : (r.roleName as string) ?? "—";
              }
              return (
                <MultiRoleSelect
                  userId={uid}
                  roleIds={memberRoleIds(r)}
                  roles={roles}
                  onSaved={() => {
                    setActionError(null);
                    invalidate();
                  }}
                  onError={(message) => setActionError(message)}
                />
              );
            },
          },
          {
            key: "isActive",
            header: "Status",
            sortable: true,
            sortAccessor: (r) => (r.isActive === false ? 0 : 1),
            render: (r) => (
              <UserStatusBadge
                active={r.isActive !== false}
                emailVerified={r.emailVerified as boolean | undefined}
              />
            ),
          },
          {
            key: "ipAllowlist",
            header: "IP restrict",
            sortable: false,
            cardHidden: true,
            render: (r) => {
              const raw = String(r.ipAllowlist ?? "").trim();
              return (
                <span className="text-xs text-fg-muted" title={raw || "No restriction"}>
                  {raw ? raw.split(",").length + " IP(s)" : "—"}
                </span>
              );
            },
          },
          ...(canInvite
            ? [
                {
                  key: "actions",
                  header: "Actions",
                  sortable: false,
                  render: (r: RbacUser) => (
                    <UserRowActions
                      user={r}
                      canInvite={canInvite}
                      onError={setActionError}
                      onClearError={() => setActionError(null)}
                      onInvalidate={invalidate}
                    />
                  ),
                } as GridColumn<RbacUser>,
              ]
            : []),
        ],
        { primaryKey: "name", hideBelowMdKeys: ["email"] },
      ),
    [
      allPageSelected,
      canInvite,
      canManageRoles,
      canSelectRows,
      roles,
      selected,
      somePageSelected,
      togglePageSelection,
      toggleRow,
    ],
  );

  const adminMenuItems = [
    {
      id: "learning",
      label: "Learning insights",
      onClick: () => router.push("/settings/learning-insights"),
    },
    {
      id: "releases",
      label: "What's New CMS",
      onClick: () => router.push("/settings/onboarding-releases"),
    },
    {
      id: "templates",
      label: "Email templates",
      onClick: () => router.push("/settings/invite-templates"),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Users"
        breadcrumb="Home / Users"
        description="Invite members, assign roles, and manage access."
        tourRoot="settings-users-header"
        actions={
          <ResponsiveActionCluster menuLabel="User actions">
            {(canManageRoles || canInvite) && (
              <>
                <Link href="/settings/module-access">
                  <Button variant="outline">Module access</Button>
                </Link>
                <Link href="/settings/roles">
                  <Button variant="outline">Manage roles</Button>
                </Link>
              </>
            )}
            {canInvite && (
              <>
                <ActionMenu items={adminMenuItems} triggerLabel="Admin tools" />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowReinvite((v) => !v)}
                >
                  {showReinvite ? "Close reinvite" : "Reinvite user"}
                </Button>
                <Link href="/settings/users/new">
                  <Button type="button">+ Add user</Button>
                </Link>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowInvite((v) => !v)}
                >
                  {showInvite ? "Close quick invite" : "Quick invite"}
                </Button>
              </>
            )}
          </ResponsiveActionCluster>
        }
      />

      {!canInvite && !canManageRoles && (
        <p className="mb-4 text-sm text-fg-muted">
          You can view users but need invite or role-management permissions to change access.
        </p>
      )}

      {canInvite && seats ? (
        <div
          className={cn(
            "mb-4 rounded-xl px-3 py-2 text-sm",
            seatsAtLimit ? warningSurfaceClasses : brandSoftClasses,
          )}
        >
          Seats: {seats.used}
          {seats.limit != null ? ` / ${seats.limit}` : " (unlimited)"} on plan{" "}
          {billingData?.result?.planCode ?? "standard"}.
          {seatsAtLimit ? " Revoke a member or upgrade before inviting." : null}{" "}
          <Link href="/settings/module-subscriptions" className={brandLinkClasses}>
            Module subscriptions
          </Link>
        </div>
      ) : null}

      {canInvite ? (
        <p className="mb-4 text-xs text-fg-muted">
          New users receive a setup email with OTP verification. Optional per-user IP allowlists
          restrict tenant API access.
        </p>
      ) : null}

      {highlightUserId && (
        <div
          className={cn(
            "mb-4 flex flex-wrap items-center gap-2 rounded-xl px-3 py-2 text-sm",
            brandSoftClasses,
          )}
        >
          <span>
            Showing user <code className="text-xs">{highlightUserId}</code>
          </span>
          <Link href="/settings/users" className={cn("font-medium hover:underline", brandLinkClasses)}>
            Clear filter
          </Link>
        </div>
      )}

      {actionError && (
        <div
          className="mb-4 flex flex-wrap items-start justify-between gap-2 rounded-lg border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger"
          role="alert"
        >
          <span>{actionError}</span>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="shrink-0 border-status-danger/30 text-status-danger hover:bg-status-danger/10"
            onClick={() => setActionError(null)}
          >
            Dismiss
          </Button>
        </div>
      )}

      {showReinvite && canInvite && (
        <Card className={cn("mb-4", warningSurfaceClasses)}>
          <CardHeader className="pb-2">
            <CardTitle>Reinvite user</CardTitle>
            <CardDescription>
              Re-add someone who was revoked from this company. They must not already be a member.
            </CardDescription>
          </CardHeader>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              reinviteMutation.mutate();
            }}
          >
            <CardContent className="grid gap-3 md:grid-cols-2">
              <FormField label="Email" required>
                <div className="flex gap-2">
                  <Input
                    type="email"
                    required
                    value={reinvite.email}
                    onChange={(e) => setReinvite((s) => ({ ...s, email: e.target.value }))}
                    placeholder="user@example.com"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    disabled={!reinvite.email.trim() || lookupEmail.isPending}
                    onClick={() => lookupEmail.mutate(reinvite.email.trim())}
                  >
                    {lookupEmail.isPending ? "…" : "Verify"}
                  </Button>
                </div>
              </FormField>
              <RoleSelectField
                value={reinvite.roleId}
                onChange={(roleId) => setReinvite((s) => ({ ...s, roleId }))}
                roles={roles}
                canManageRoles={canManageRoles}
                returnTo="/settings/users"
              />
            </CardContent>
            <CardFooter className="gap-2 border-t-0 pt-0">
              <Button
                type="submit"
                disabled={
                  reinviteMutation.isPending ||
                  !reinvite.email.trim() ||
                  !reinvite.roleId
                }
              >
                {reinviteMutation.isPending ? "Reinviting…" : "Reinvite"}
              </Button>
              {(reinviteUserIdParam || reinviteEmailParam) && (
                <Link href="/settings/users">
                  <Button type="button" variant="outline">
                    Clear
                  </Button>
                </Link>
              )}
            </CardFooter>
          </form>
        </Card>
      )}

      {showInvite && canInvite && (
        <div className="mb-4">
          <UserInviteForm
            title="Quick invite"
            description="Send an invitation email with access to this company."
            submitLabel="Send invite"
            cancelHref=""
            returnTo="/settings/users"
            onSuccess={() => {
              setShowInvite(false);
              invalidate();
            }}
          />
        </div>
      )}

      <ListToolbar
        search={search}
        onSearchChange={setSearch}
        searchPlaceholder={
          highlightUserId ? "Clear user filter to search" : "Search by email or name…"
        }
        searchDisabled={Boolean(highlightUserId)}
      >
        <div className="w-40">
          <FormField label="Status">
            <Select
              value={statusFilter}
              onChange={(e) =>
                setStatusFilter(e.target.value as "" | "active" | "inactive")
              }
            >
              <option value="">All</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </Select>
          </FormField>
        </div>
      </ListToolbar>

      {selected.size > 0 && canSelectRows && (
        <Card variant="default" className={cn("mb-4", brandSoftClasses)}>
          <CardContent className="flex flex-wrap items-end gap-3 p-4">
            <span className="self-center text-sm font-medium text-fg">
              {selected.size} selected
            </span>
            {canManageRoles && (
              <>
                <div className="min-w-[12rem]">
                  <RoleSelectField
                    value={bulkRoleId}
                    onChange={setBulkRoleId}
                    roles={roles}
                    canManageRoles={canManageRoles}
                    returnTo="/settings/users"
                  />
                </div>
                <Button
                  type="button"
                  disabled={!bulkRoleId || bulkAssign.isPending}
                  onClick={() => bulkAssign.mutate()}
                >
                  Assign role
                </Button>
              </>
            )}
            {canInvite && (
              <Button
                type="button"
                variant="outline"
                disabled={bulkRevoke.isPending}
                onClick={() => {
                  if (!confirm(`Revoke ${selected.size} user(s)?`)) return;
                  bulkRevoke.mutate();
                }}
              >
                Revoke
              </Button>
            )}
            <Button type="button" variant="outline" onClick={() => setSelected(new Set())}>
              Clear selection
            </Button>
          </CardContent>
        </Card>
      )}

      <EnterpriseGrid<RbacUser>
        columns={columns}
        rows={rows}
        loading={isLoading}
        fetching={isFetching}
        error={error}
        emptyMessage={
          search || statusFilter || highlightUserId
            ? "No users match your filters."
            : "No users yet."
        }
        getRowId={(row) => memberUserId(row)}
        rowClassName={(r) =>
          highlightUserId && memberUserId(r) === highlightUserId
            ? brandRowHighlightClasses
            : undefined
        }
        pagination={{
          page,
          pageSize,
          totalItems: total,
          onPageChange: setPage,
        }}
        tourTarget="settings-users-grid"
      />
    </div>
  );
}
