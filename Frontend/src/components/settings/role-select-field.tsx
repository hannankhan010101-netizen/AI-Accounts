"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { FormField } from "@/components/ui/form-field";
import { Select } from "@/components/ui/select";
import type { RbacRole } from "@/lib/api/tenant";
import { brandLinkClasses } from "@/lib/design-tokens/brand-surfaces";

export const CREATE_ROLE_OPTION = "__create_role__";

type RoleSelectFieldProps = {
  value: string;
  onChange: (roleId: string) => void;
  roles: RbacRole[];
  canManageRoles?: boolean;
  returnTo?: string;
  disabled?: boolean;
};

export function RoleSelectField({
  value,
  onChange,
  roles,
  canManageRoles = false,
  returnTo,
  disabled = false,
}: RoleSelectFieldProps) {
  const router = useRouter();
  const createHref =
    "/settings/roles/new" +
    (returnTo ? `?returnTo=${encodeURIComponent(returnTo)}` : "");

  return (
    <FormField label="Role" required>
      <Select
        value={value}
        disabled={disabled}
        onChange={(e) => {
          const next = e.target.value;
          if (next === CREATE_ROLE_OPTION) {
            router.push(createHref);
            return;
          }
          onChange(next);
        }}
      >
        <option value="">Select role</option>
        {roles.map((role) => (
          <option key={role.id} value={role.id}>
            {role.name}
          </option>
        ))}
        {canManageRoles ? (
          <option value={CREATE_ROLE_OPTION}>+ Add new role…</option>
        ) : null}
      </Select>
      {roles.length <= 1 && canManageRoles ? (
        <p className="mt-1 text-xs text-fg-muted">
          Add more roles for different access levels.{" "}
          <Link href={createHref} className={brandLinkClasses}>
            Create role
          </Link>
        </p>
      ) : null}
    </FormField>
  );
}
