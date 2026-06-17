"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { invalidateTenantQueries, useTenantReferenceQuery } from "@/lib/api/tenant-query";

import { RoleSelectField } from "@/components/settings/role-select-field";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { rbacApi } from "@/lib/api/tenant";
import {
  hasPermission,
  PERM_ROLES_MANAGE,
  PERM_USERS_INVITE,
} from "@/lib/rbac/permissions";
export type UserInviteFormValues = {
  email: string;
  firstName: string;
  lastName: string;
  roleId: string;
};

const emptyValues: UserInviteFormValues = {
  email: "",
  firstName: "",
  lastName: "",
  roleId: "",
};

type UserInviteFormProps = {
  title?: string;
  description?: string;
  submitLabel?: string;
  cancelHref?: string;
  returnTo?: string;
  onSuccess?: () => void;
};

export function UserInviteForm({
  title = "Add user",
  description = "Invite a team member by email. They receive setup instructions with OTP verification.",
  submitLabel = "Save and send invite",
  cancelHref = "/settings/users",
  returnTo = "/settings/users/new",
  onSuccess,
}: UserInviteFormProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [values, setValues] = useState<UserInviteFormValues>(emptyValues);
  const [error, setError] = useState<string | null>(null);

  const { data: permsData } = useTenantReferenceQuery(["my-permissions"], () => rbacApi.getMyPermissions());
  const myPerms = permsData?.result?.permissions ?? [];
  const canInvite = hasPermission(myPerms, PERM_USERS_INVITE);
  const canManageRoles = hasPermission(myPerms, PERM_ROLES_MANAGE);

  const { data: rolesData } = useTenantReferenceQuery(["rbac-roles"], () => rbacApi.listRoles(), { enabled: canInvite });
  const roles = rolesData?.result ?? [];

  const inviteMutation = useMutation({
    mutationFn: () => rbacApi.inviteUser(values),
    onSuccess: () => {
      setValues(emptyValues);
      setError(null);
      void invalidateTenantQueries(queryClient, "rbac-users");
      if (onSuccess) {
        onSuccess();
      } else {
        router.push("/settings/users");
      }
    },
    onError: (e: Error) => setError(e.message),
  });

  if (!canInvite) {
    return (
      <Card>
        <CardContent className="py-6 text-sm text-fg-muted">
          You do not have permission to invite users. Ask an administrator to grant{" "}
          <code className="text-xs">settings.users.invite</code>.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card variant="elevated">
      <CardHeader className="pb-2">
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (!values.roleId) {
            setError("Select a role for this user.");
            return;
          }
          inviteMutation.mutate();
        }}
      >
        <CardContent className="grid gap-3 md:grid-cols-2">
          <FormField label="First name" required>
            <Input
              required
              value={values.firstName}
              onChange={(e) =>
                setValues((s) => ({ ...s, firstName: e.target.value }))
              }
            />
          </FormField>
          <FormField label="Last name" required>
            <Input
              required
              value={values.lastName}
              onChange={(e) =>
                setValues((s) => ({ ...s, lastName: e.target.value }))
              }
            />
          </FormField>
          <FormField label="Email" required>
            <Input
              type="email"
              required
              autoComplete="email"
              value={values.email}
              onChange={(e) => setValues((s) => ({ ...s, email: e.target.value }))}
            />
          </FormField>
          <RoleSelectField
            value={values.roleId}
            onChange={(roleId) => setValues((s) => ({ ...s, roleId }))}
            roles={roles}
            canManageRoles={canManageRoles}
            returnTo={returnTo}
          />
        </CardContent>
        {error ? (
          <CardContent className="pt-0">
            <p className="text-sm text-status-danger" role="alert">
              {error}
            </p>
          </CardContent>
        ) : null}
        <CardFooter className="gap-2 border-t-0 pt-0">
          <Button
            type="submit"
            disabled={
              inviteMutation.isPending ||
              !values.email.trim() ||
              !values.firstName.trim() ||
              !values.lastName.trim() ||
              !values.roleId
            }
          >
            {inviteMutation.isPending ? "Saving…" : submitLabel}
          </Button>
          {cancelHref ? (
            <Link href={cancelHref}>
              <Button type="button" variant="outline">
                Cancel
              </Button>
            </Link>
          ) : null}
        </CardFooter>
      </form>
    </Card>
  );
}
