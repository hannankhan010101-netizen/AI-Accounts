/** Edit role — catalog §12.4 */
"use client";

import { RoleEditorForm } from "@/components/settings/role-editor-form";

export default function EditRolePage({ params }: { params: { roleId: string } }) {
  return <RoleEditorForm mode="edit" roleId={params.roleId} />;
}
