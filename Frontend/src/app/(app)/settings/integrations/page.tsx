/** Integration readiness — FBR, PayPro, Kuickpay (no secrets). */
"use client";

import Link from "next/link";

import { IntegrationReadinessBanner } from "@/components/settings/integration-readiness-banner";
import { PageHeader } from "@/components/ui/page-header";

export default function IntegrationsStatusPage() {
  return (
    <div>
      <PageHeader
        title="Integrations"
        breadcrumb="Settings / Integrations"
        description="Production credentials and queue health for FBR/PRAL and online payment providers."
      />
      <IntegrationReadinessBanner />
      <ul className="space-y-2 text-sm">
        <li>
          <Link href="/settings/fbr-errors" className="text-brand hover:underline">
            FBR submission errors
          </Link>
          {" — retry queue and failed PRAL submissions"}
        </li>
        <li>
          <Link href="/settings/online-payments" className="text-brand hover:underline">
            Online payments
          </Link>
          {" — PayPro / Kuickpay checkout and webhooks"}
        </li>
      </ul>
    </div>
  );
}
