/** Sales invoice detail — catalog §5.4 (draft edit, approve, goods issue, FBR). */
"use client";
import { useTenantReferenceQuery, useTenantDetailQuery, invalidateTenantQueries, useTenantListQuery } from "@/lib/api/tenant-query";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import Decimal from "decimal.js";

import { StatusBadge } from "@/components/app/status-badge";
import { AttachmentPanel } from "@/components/patterns/attachment-panel";
import {
  DetailAlertBanner,
  DocumentDetailShell,
} from "@/components/patterns/document-detail-shell";
import { DocumentLinesGrid } from "@/components/patterns/document-lines-grid";
import { Button } from "@/components/ui/button";
import { FormSection } from "@/components/ui/form-section";
import { useToast } from "@/components/ui/toast";
import { useCustomerNameMap } from "@/lib/hooks/use-party-name-map";
import { salesApi, integrationsApi, appSettingsApi } from "@/lib/api/tenant";
import { DetailPageLoading } from "@/components/ui/detail-page-loading";

function fmt(v: string): string {
  try {
    return new Decimal(v).toFixed(2);
  } catch {
    return v;
  }
}

export default function SalesInvoiceDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const toast = useToast();
  const customerNames = useCustomerNameMap();
  const [voidSuccess, setVoidSuccess] = useState(false);
  const { data, isLoading, error } = useTenantDetailQuery(["sales-invoice", params.id], () => salesApi.getInvoice(params.id), { enabled: !!params.id });
  const approve = useMutation({
    mutationFn: () => salesApi.approveInvoice(params.id),
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, "sales-invoice", params.id);
      void invalidateTenantQueries(queryClient, "sales-invoices");
    },
  });
  const goodsIssue = useMutation({
    mutationFn: () => salesApi.createGoodsIssue(params.id),
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, "sales-invoice", params.id);
      void invalidateTenantQueries(queryClient, "goods-issue", params.id);
    },
  });
  const invStatus = (data?.result as { status?: string } | undefined)?.status;
  const { data: giData } = useTenantListQuery(["goods-issue", params.id], () => salesApi.getGoodsIssue(params.id),
    { enabled: !!params.id && invStatus === "posted",
    retry: false });
  const { data: fbrData } = useTenantListQuery(["fbr", params.id], () => salesApi.getFbrStatus(params.id),
    { enabled: !!params.id && invStatus === "posted",
    retry: false });
  const { data: integrationsData } = useTenantReferenceQuery(["integrations-readiness"], () => integrationsApi.getReadiness(), { enabled: invStatus === "posted" });
  const { data: emailSettingsData } = useTenantReferenceQuery(["email-settings"], () => appSettingsApi.getEmailSettings());
  const invoiceEmailEnabled =
    emailSettingsData?.result?.sendInvoiceEmail === true;
  const emailInvoice = useMutation({
    mutationFn: () => salesApi.emailInvoice(params.id),
    onSuccess: (res) => {
      const sent = res.result.emailSent;
      if (sent) {
        toast.success(`Invoice emailed to ${res.result.to}.`);
      } else {
        toast.error("Email could not be sent (check Brevo/SMTP settings).");
      }
    },
  });
  const submitFbr = useMutation({
    mutationFn: () => salesApi.submitFbr(params.id),
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, "fbr", params.id);
    },
  });
  const pollFbr = useMutation({
    mutationFn: () => salesApi.pollFbr(params.id),
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, "fbr", params.id);
    },
  });
  const retryFbr = useMutation({
    mutationFn: () => salesApi.retryFbr(params.id),
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, "fbr", params.id);
    },
  });
  const voidInvoice = useMutation({
    mutationFn: () => salesApi.voidInvoice(params.id),
    onSuccess: async () => {
      setVoidSuccess(true);
      await invalidateTenantQueries(queryClient, "sales-invoice", params.id);
      await invalidateTenantQueries(queryClient, "sales-invoices");
    },
  });
  const copyInvoice = useMutation({
    mutationFn: () => salesApi.copyInvoice(params.id),
    onSuccess: (res) => {
      void invalidateTenantQueries(queryClient, "sales-invoices");
      router.push(`/sales/invoices/${res.result.id}`);
    },
  });
  const fbrStatus = (fbrData?.result as { status?: string } | null | undefined)?.status;
  const fbrLive = integrationsData?.result.fbr.ready;
  const fbrMode = integrationsData?.result.fbr.mode;

  if (isLoading) return <DetailPageLoading />;
  if (error instanceof Error)
    return (
      <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
        {error.message}
      </div>
    );

  const inv = data?.result;
  if (!inv) return null;

  const status = inv.status ?? "posted";
  const isDraft = status === "draft";
  const isPosted = status === "posted" && !!inv.journalId;
  const isVoided = status === "voided" || status === "reversed";
  const canVoid = isPosted && !isVoided;
  const hasGoodsIssue = !!giData?.result;

  const hasBanners =
    voidSuccess ||
    voidInvoice.isError ||
    approve.isError ||
    goodsIssue.isError ||
    emailInvoice.isError;

  return (
    <DocumentDetailShell
      title={`Invoice ${inv.documentNumber ?? inv.id}`}
      breadcrumb="Sell / Invoices / Detail"
      metaFields={[
        { label: "Invoice no.", value: inv.documentNumber ?? "—" },
        { label: "Date", value: new Date(inv.invoiceDate).toLocaleDateString() },
        {
          label: "Customer",
          value: customerNames.get(inv.customerId) ?? inv.customerId,
        },
        { label: "Status", value: <StatusBadge status={status} /> },
        {
          label: "GL",
          value: inv.journalId ? (
            <Link
              href={`/settings/journals/${inv.journalId}`}
              className="text-brand hover:underline"
            >
              View journal
            </Link>
          ) : (
            <span className="text-fg-muted">Not posted</span>
          ),
        },
      ]}
      banners={
        hasBanners ? (
          <div className="space-y-2">
            {voidSuccess ? (
              <DetailAlertBanner variant="success">
                Invoice voided. GL reversal posted where applicable.
              </DetailAlertBanner>
            ) : null}
            {voidInvoice.isError ? (
              <DetailAlertBanner variant="error">
                {voidInvoice.error instanceof Error
                  ? voidInvoice.error.message
                  : "Void failed"}
              </DetailAlertBanner>
            ) : null}
            {approve.isError ? (
              <DetailAlertBanner variant="error">
                {approve.error instanceof Error ? approve.error.message : "Approve failed"}
              </DetailAlertBanner>
            ) : null}
            {goodsIssue.isError ? (
              <DetailAlertBanner variant="error">
                {goodsIssue.error instanceof Error ? goodsIssue.error.message : "Goods issue failed"}
              </DetailAlertBanner>
            ) : null}
            {emailInvoice.isError ? (
              <DetailAlertBanner variant="error">
                {emailInvoice.error instanceof Error ? emailInvoice.error.message : "Email failed"}
              </DetailAlertBanner>
            ) : null}
          </div>
        ) : undefined
      }
      actions={
        <>
          <Button
            type="button"
            variant="outline"
            disabled={copyInvoice.isPending}
            onClick={() => copyInvoice.mutate()}
          >
            {copyInvoice.isPending ? "Copying…" : "Copy"}
          </Button>
          {isDraft ? (
            <>
              <Link
                href={`/sales/invoices/${inv.id}/edit`}
                className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
              >
                Edit draft
              </Link>
              <Button
                type="button"
                disabled={approve.isPending}
                onClick={() => approve.mutate()}
              >
                {approve.isPending ? "Posting…" : "Approve & post to GL"}
              </Button>
            </>
          ) : null}
          {isPosted && !hasGoodsIssue ? (
            <Button
              type="button"
              variant="secondary"
              disabled={goodsIssue.isPending}
              onClick={() => goodsIssue.mutate()}
            >
              {goodsIssue.isPending ? "Issuing…" : "Issue goods / COGS"}
            </Button>
          ) : null}
          {hasGoodsIssue ? (
            <span className="inline-flex h-9 items-center rounded-md border border-border bg-canvas px-3 text-sm text-fg-muted">
              Goods issued
            </span>
          ) : null}
          {canVoid ? (
            <Button
              type="button"
              variant="outline"
              disabled={voidInvoice.isPending}
              onClick={() => {
                if (
                  !window.confirm(
                    "Void this posted invoice? GL will be reversed and the document marked void. This cannot be undone.",
                  )
                ) {
                  return;
                }
                voidInvoice.mutate();
              }}
            >
              {voidInvoice.isPending ? "Voiding…" : "Void"}
            </Button>
          ) : null}
          {isVoided ? (
            <Link
              href="/sales/invoices/new"
              className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
            >
              Create replacement
            </Link>
          ) : null}
          <Link
            href={`/print/sales-invoice/${inv.id}`}
            target="_blank"
            className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-brand hover:bg-canvas"
          >
            Print
          </Link>
          {!isVoided && invoiceEmailEnabled ? (
            <Button
              type="button"
              variant="outline"
              disabled={emailInvoice.isPending}
              onClick={() => emailInvoice.mutate()}
            >
              {emailInvoice.isPending ? "Sending…" : "Email customer"}
            </Button>
          ) : null}
        </>
      }
    >
      {isPosted ? (
        <FormSection title="FBR digital invoicing">
          <div className="flex flex-wrap items-center justify-end gap-2">
            <span
              className={
                fbrLive
                  ? "rounded-full bg-status-success/15 px-2 py-0.5 text-xs text-status-success"
                  : "rounded-full bg-status-warning/15 px-2 py-0.5 text-xs text-status-warning"
              }
            >
              {fbrLive ? "Live PRAL" : fbrMode === "stub" ? "Stub mode" : "Not configured"}
            </span>
          </div>
          <p className="text-sm text-fg-muted">
            Status: {fbrStatus ?? "not submitted"}
            {(fbrData?.result as { fbrReference?: string } | null | undefined)?.fbrReference
              ? ` · Ref ${(fbrData?.result as { fbrReference?: string }).fbrReference}`
              : ""}
            {(fbrData?.result as { lastError?: string } | undefined)?.lastError
              ? ` · ${(fbrData?.result as { lastError?: string }).lastError}`
              : ""}
          </p>
          <div className="flex flex-wrap gap-2">
            {fbrStatus !== "submitted" ? (
              <Button
                type="button"
                size="sm"
                disabled={submitFbr.isPending}
                onClick={() => submitFbr.mutate()}
              >
                {submitFbr.isPending ? "Submitting…" : "Submit to FBR"}
              </Button>
            ) : null}
            {fbrStatus === "error" || fbrStatus === "pending" ? (
              <Button
                type="button"
                size="sm"
                variant="outline"
                disabled={retryFbr.isPending}
                onClick={() => retryFbr.mutate()}
              >
                {retryFbr.isPending ? "Retrying…" : "Retry submission"}
              </Button>
            ) : null}
            {fbrStatus === "submitted" ? (
              <Button
                type="button"
                size="sm"
                variant="outline"
                disabled={pollFbr.isPending}
                onClick={() => pollFbr.mutate()}
              >
                {pollFbr.isPending ? "Polling…" : "Poll status"}
              </Button>
            ) : null}
          </div>
          {submitFbr.isError || pollFbr.isError || retryFbr.isError ? (
            <p className="text-sm text-status-danger">
              {(submitFbr.error ?? pollFbr.error ?? retryFbr.error) instanceof Error
                ? (submitFbr.error ?? pollFbr.error ?? retryFbr.error)?.message
                : "FBR action failed"}
            </p>
          ) : null}
          {!fbrLive ? (
            <p className="text-xs text-fg-muted">
              Stub submissions work for UAT. For live PRAL, configure{" "}
              <Link href="/settings/integrations" className="text-brand hover:underline">
                Integration status
              </Link>
              .
            </p>
          ) : null}
        </FormSection>
      ) : null}

      <DocumentLinesGrid
        lines={inv.lines}
        totalAmount={inv.totalAmount}
        showProject
        showGst
        descriptionDocType="SI"
        showBatchExpiry
        lastRateContext={{
          docType: "SI",
          partyKind: "customer",
          partyId: inv.customerId,
        }}
      />

      <AttachmentPanel entityType="sales_invoice" entityId={inv.id} />
    </DocumentDetailShell>
  );
}
