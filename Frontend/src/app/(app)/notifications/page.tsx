"use client";

import Link from "next/link";
import { useEffect } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { useToast } from "@/components/ui/toast";
import { useTenantListQuery } from "@/lib/api/tenant-query";
import { notificationsApi } from "@/lib/api/tenant";
import { useCompany } from "@/lib/auth/company-context";
import { markNotificationsSeen } from "@/lib/notifications/seen";
import { useMutation } from "@tanstack/react-query";

export default function NotificationsPage() {
  const toast = useToast();
  const { companyId } = useCompany();
  const { data, isLoading, error, refetch } = useTenantListQuery(
    ["notifications"],
    () => notificationsApi.list(),
  );

  const items = data?.result.items ?? [];
  const itemIdsKey = items.map((item) => item.id).join("|");

  useEffect(() => {
    if (!companyId || !itemIdsKey) return;
    markNotificationsSeen(companyId, itemIdsKey.split("|"));
  }, [companyId, itemIdsKey]);

  const digestMutation = useMutation({
    mutationFn: () => notificationsApi.runExpiryDigest(),
    onSuccess: (res) => toast.success(res.result.message),
    onError: (err: Error) => toast.error(err.message),
  });

  return (
    <div>
      <PageHeader
        title="Notifications"
        breadcrumb="Home / Notifications"
        description="Batch expiry and inventory alerts for your company."
        actions={
          <Button
            variant="outline"
            size="sm"
            disabled={digestMutation.isPending}
            onClick={() => digestMutation.mutate()}
          >
            {digestMutation.isPending ? "Sending…" : "Email digest"}
          </Button>
        }
      />

      {isLoading ? (
        <p className="text-sm text-fg-muted">Loading…</p>
      ) : error ? (
        <p className="text-sm text-status-danger">Could not load notifications.</p>
      ) : items.length === 0 ? (
        <Card variant="glass" className="p-6 text-center text-sm text-fg-muted">
          No batch expiry alerts right now.
        </Card>
      ) : (
        <ul className="space-y-3">
          {items.map((item) => (
            <li key={item.id}>
              <Card variant="glass" className="p-4">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-sm font-semibold text-fg">{item.title}</h2>
                      <Badge variant={item.severity === "critical" ? "danger" : "warning"}>
                        {item.severity === "critical" ? "Critical" : "Warning"}
                      </Badge>
                    </div>
                    <p className="mt-1 text-sm text-fg-muted">{item.message}</p>
                  </div>
                  <Button variant="outline" size="sm" asChild>
                    <Link href={item.href as "/inventory/batches"}>Review</Link>
                  </Button>
                </div>
              </Card>
            </li>
          ))}
        </ul>
      )}

      <p className="mt-4 text-xs text-fg-muted">
        <button type="button" className="text-brand hover:underline" onClick={() => refetch()}>
          Refresh
        </button>
      </p>
    </div>
  );
}
