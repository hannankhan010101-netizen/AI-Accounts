"use client";

import { Button } from "@/components/ui/button";
import { ActionMenu, type ActionMenuItem } from "@/components/ui/action-menu";
import { useToast } from "@/components/ui/toast";
import { rbacApi, type RbacUser } from "@/lib/api/tenant";

function memberUserId(row: RbacUser): string {
  return String(row.userId ?? row.id);
}

interface UserRowActionsProps {
  user: RbacUser;
  canInvite: boolean;
  onError: (message: string) => void;
  onClearError: () => void;
  onInvalidate: () => void;
}

export function UserRowActions({
  user,
  canInvite,
  onError,
  onClearError,
  onInvalidate,
}: UserRowActionsProps) {
  const toast = useToast();
  if (!canInvite) return null;

  const uid = memberUserId(user);

  async function resendEmail() {
    try {
      const res = await rbacApi.resendUserInvite(uid);
      onClearError();
      const kind = res.result.emailType;
      const sent = res.result.emailSent;
      toast.success(
        sent
          ? `${kind === "welcome" ? "Welcome" : "Setup"} email sent.`
          : "Email could not be sent (check SMTP settings).",
      );
    } catch (e) {
      onError(e instanceof Error ? e.message : "Resend failed");
    }
  }

  async function revoke() {
    if (!confirm("Revoke this user from the company?")) return;
    try {
      await rbacApi.revokeUserMembership(uid);
      onInvalidate();
    } catch (e) {
      onError(e instanceof Error ? e.message : "Revoke failed");
    }
  }

  async function activate() {
    try {
      await rbacApi.reactivateUser(uid);
      onInvalidate();
    } catch (e) {
      onError(e instanceof Error ? e.message : "Reactivate failed");
    }
  }

  async function deactivate() {
    if (!confirm("Deactivate account globally?")) return;
    try {
      await rbacApi.deactivateUser(uid);
      onInvalidate();
    } catch (e) {
      onError(e instanceof Error ? e.message : "Deactivate failed");
    }
  }

  async function editIpAllowlist() {
    const current = String(user.ipAllowlist ?? "").trim();
    const next = window.prompt(
      "Comma-separated IPs allowed for API access (leave empty for no restriction):",
      current,
    );
    if (next === null) return;
    try {
      await rbacApi.updateIpAllowlist(uid, next.trim() || null);
      onClearError();
      onInvalidate();
    } catch (e) {
      onError(e instanceof Error ? e.message : "IP allowlist update failed");
    }
  }

  const menuItems: ActionMenuItem[] = [
    { id: "resend", label: "Resend email", onClick: () => void resendEmail() },
    { id: "ip", label: "IP allowlist", onClick: () => void editIpAllowlist() },
    { id: "revoke", label: "Revoke membership", variant: "danger", onClick: () => void revoke() },
    user.isActive === false
      ? { id: "activate", label: "Activate", onClick: () => void activate() }
      : { id: "deactivate", label: "Deactivate", variant: "danger", onClick: () => void deactivate() },
  ];

  const label = `${user.firstName ?? ""} ${user.lastName ?? ""}`.trim() || String(user.email ?? "user");

  return (
    <>
      <div className="hidden flex-wrap gap-1 lg:flex">
        <Button type="button" variant="outline" size="sm" onClick={() => void resendEmail()}>
          Resend email
        </Button>
        <Button type="button" variant="outline" size="sm" onClick={() => void editIpAllowlist()}>
          IP allowlist
        </Button>
        <Button type="button" variant="outline" size="sm" onClick={() => void revoke()}>
          Revoke
        </Button>
        {user.isActive === false ? (
          <Button type="button" variant="outline" size="sm" onClick={() => void activate()}>
            Activate
          </Button>
        ) : (
          <Button type="button" variant="outline" size="sm" onClick={() => void deactivate()}>
            Deactivate
          </Button>
        )}
      </div>
      <div className="lg:hidden">
        <ActionMenu items={menuItems} triggerLabel={`Actions for ${label}`} />
      </div>
    </>
  );
}
