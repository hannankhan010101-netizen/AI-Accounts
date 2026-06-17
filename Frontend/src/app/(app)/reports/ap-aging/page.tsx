/** Accounts Payable Aging — catalog §10.9. */
import { AgingReport } from "@/components/app/aging-report";
import { PageHeader } from "@/components/ui/page-header";

export default function ApAgingPage() {
  return (
    <div>
      <PageHeader
        title="AP Aging"
        breadcrumb="Home / Reports / Accounts Payable / Aging"
        description="Open balance per supplier, bucketed by oldest open bill age."
      />
      <AgingReport kind="ap" statementRoute="/reports/supplier-statement" />
    </div>
  );
}
