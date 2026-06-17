/** Invite & welcome email templates — P30/P31/P39 */
"use client";
import { invalidateTenantQueries, useTenantReferenceQuery } from "@/lib/api/tenant-query";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { rbacApi } from "@/lib/api/tenant";
import { hasPermission, PERM_USERS_INVITE } from "@/lib/rbac/permissions";


type TemplateFields = {
  subject: string;
  introText: string;
  introHtml: string;
};

type PreviewResult = {
  preview: TemplateFields;
  sampleValues: Record<string, string>;
};

function emptyTemplate(): TemplateFields {
  return { subject: "", introText: "", introHtml: "" };
}

function TemplateForm({
  label,
  kind,
  fields,
  onChange,
  placeholders,
  disabled,
  onSave,
  onReset,
  onPreview,
  saving,
  preview,
  previewLoading,
}: {
  label: string;
  kind: "invite" | "welcome";
  fields: TemplateFields;
  onChange: (next: TemplateFields) => void;
  placeholders: string[];
  disabled: boolean;
  onSave: () => void;
  onReset: () => void;
  onPreview: () => void;
  saving: boolean;
  preview: PreviewResult | null;
  previewLoading: boolean;
}) {
  return (
    <section className="rounded-lg border border-border bg-surface p-4">
      <h2 className="mb-3 text-sm font-semibold text-fg">{label}</h2>
      <p className="mb-4 text-xs text-fg-muted">
        Placeholders: {placeholders.map((p) => `{{${p}}}`).join(", ")}
      </p>
      <div className="grid gap-3">
        <FormField label="Subject">
          <Input
            value={fields.subject}
            disabled={disabled}
            onChange={(e) => onChange({ ...fields, subject: e.target.value })}
          />
        </FormField>
        <FormField label="Intro (plain text)">
          <textarea
            className="min-h-[100px] w-full rounded-md border border-border px-3 py-2 text-sm"
            value={fields.introText}
            disabled={disabled}
            onChange={(e) => onChange({ ...fields, introText: e.target.value })}
          />
        </FormField>
        <FormField label="Intro (HTML)">
          <textarea
            className="min-h-[100px] w-full rounded-md border border-border px-3 py-2 font-mono text-sm"
            value={fields.introHtml}
            disabled={disabled}
            onChange={(e) => onChange({ ...fields, introHtml: e.target.value })}
          />
        </FormField>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <Button type="button" variant="outline" disabled={previewLoading} onClick={onPreview}>
          {previewLoading ? "Rendering…" : "Preview"}
        </Button>
        {!disabled && (
          <>
            <Button type="button" disabled={saving} onClick={onSave}>
              {saving ? "Saving…" : "Save"}
            </Button>
            <Button type="button" variant="outline" onClick={onReset}>
              Reset to defaults
            </Button>
          </>
        )}
      </div>
      {disabled && (
        <p className="mt-3 text-sm text-fg-muted">
          You need <code>settings.users.invite</code> to edit templates.
        </p>
      )}
      {preview && (
        <div className="mt-4 rounded-md border border-border bg-canvas p-3 text-sm">
          <p className="mb-2 font-medium text-fg">Preview ({kind})</p>
          <p className="text-xs text-fg-muted">
            Sample values:{" "}
            {Object.entries(preview.sampleValues)
              .map(([k, v]) => `${k}=${v}`)
              .join(", ")}
          </p>
          <p className="mt-2">
            <span className="font-medium">Subject:</span> {preview.preview.subject}
          </p>
          <pre className="mt-2 whitespace-pre-wrap text-xs text-fg">
            {preview.preview.introText}
          </pre>
          <div
            className="prose prose-sm dark:prose-invert mt-3 max-w-none rounded border border-border bg-surface-elevated p-2 text-fg"
            dangerouslySetInnerHTML={{ __html: preview.preview.introHtml }}
          />
        </div>
      )}
    </section>
  );
}

export default function InviteTemplatesPage() {
  const queryClient = useQueryClient();
  const [invite, setInvite] = useState<TemplateFields>(emptyTemplate());
  const [welcome, setWelcome] = useState<TemplateFields>(emptyTemplate());
  const [invitePreview, setInvitePreview] = useState<PreviewResult | null>(null);
  const [welcomePreview, setWelcomePreview] = useState<PreviewResult | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { data: permsData } = useTenantReferenceQuery(["my-permissions"], () => rbacApi.getMyPermissions());
  const canEdit = hasPermission(permsData?.result?.permissions ?? [], PERM_USERS_INVITE);

  const { data, isLoading } = useTenantReferenceQuery(["invite-email-template"], () => rbacApi.getInviteEmailTemplate());

  const defaults = data?.result?.defaults;
  const placeholders = data?.result?.placeholders;

  useEffect(() => {
    if (!data?.result) return;
    const inv = data.result.invite;
    const wel = data.result.welcome;
    setInvite({
      subject: inv.subject ?? "",
      introText: inv.introText ?? "",
      introHtml: inv.introHtml ?? "",
    });
    setWelcome({
      subject: wel.subject ?? "",
      introText: wel.introText ?? "",
      introHtml: wel.introHtml ?? "",
    });
  }, [data]);

  const saveInvite = useMutation({
    mutationFn: () => rbacApi.updateInviteEmailTemplate(invite),
    onSuccess: () => {
      setMessage("Invite template saved.");
      setError(null);
      void invalidateTenantQueries(queryClient, "invite-email-template");
    },
    onError: (e: Error) => setError(e.message),
  });

  const saveWelcome = useMutation({
    mutationFn: () => rbacApi.updateWelcomeEmailTemplate(welcome),
    onSuccess: () => {
      setMessage("Welcome template saved.");
      setError(null);
      void invalidateTenantQueries(queryClient, "invite-email-template");
    },
    onError: (e: Error) => setError(e.message),
  });

  const previewInvite = useMutation({
    mutationFn: () =>
      rbacApi.previewInviteEmailTemplate({ kind: "invite", ...invite }),
    onSuccess: (res) => {
      setInvitePreview(res.result);
      setError(null);
    },
    onError: (e: Error) => setError(e.message),
  });

  const previewWelcome = useMutation({
    mutationFn: () =>
      rbacApi.previewInviteEmailTemplate({ kind: "welcome", ...welcome }),
    onSuccess: (res) => {
      setWelcomePreview(res.result);
      setError(null);
    },
    onError: (e: Error) => setError(e.message),
  });

  return (
    <div>
      <PageHeader
        title="Invite email templates"
        breadcrumb="Home / Settings / Invite templates"
        description="Customize setup and welcome emails sent when inviting users (§12.3)."
        actions={
          <Link href="/settings/users">
            <Button variant="outline">Users</Button>
          </Link>
        }
      />

      {error && (
        <div className="mb-4 rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
          {error}
        </div>
      )}
      {message && (
        <div className="mb-4 rounded-md border border-status-success/30 bg-status-success/10 px-3 py-2 text-sm text-status-success">
          {message}
        </div>
      )}

      {isLoading ? (
        <WorkspaceLoading />
      ) : (
        <div className="grid max-w-3xl gap-6">
          <TemplateForm
            label="Invite / set-password email"
            kind="invite"
            fields={invite}
            onChange={setInvite}
            placeholders={placeholders?.invite ?? []}
            disabled={!canEdit}
            saving={saveInvite.isPending}
            onSave={() => saveInvite.mutate()}
            onReset={() => setInvite(defaults?.invite ?? emptyTemplate())}
            onPreview={() => previewInvite.mutate()}
            previewLoading={previewInvite.isPending}
            preview={invitePreview}
          />
          <TemplateForm
            label="Welcome email (verified users)"
            kind="welcome"
            fields={welcome}
            onChange={setWelcome}
            placeholders={placeholders?.welcome ?? []}
            disabled={!canEdit}
            saving={saveWelcome.isPending}
            onSave={() => saveWelcome.mutate()}
            onReset={() => setWelcome(defaults?.welcome ?? emptyTemplate())}
            onPreview={() => previewWelcome.mutate()}
            previewLoading={previewWelcome.isPending}
            preview={welcomePreview}
          />
        </div>
      )}
    </div>
  );
}
