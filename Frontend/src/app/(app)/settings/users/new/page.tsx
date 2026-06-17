/** Add user — catalog §12.3.2 */
"use client";

import Link from "next/link";

import { UserInviteForm } from "@/components/settings/user-invite-form";
import { PageHeader } from "@/components/ui/page-header";

export default function AddUserPage() {
  return (
    <div>
      <PageHeader
        title="Add user"
        breadcrumb="Home / Users / Add user"
        description="Create a company member and assign a role."
        actions={
          <Link href="/settings/users">
            <span className="text-sm font-medium text-brand hover:underline">
              Back to users
            </span>
          </Link>
        }
      />
      <UserInviteForm returnTo="/settings/users/new" />
    </div>
  );
}
