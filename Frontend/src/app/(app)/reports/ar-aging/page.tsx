/** Accounts Receivable Aging — catalog §10.9. */
import { AgingReport } from "@/components/app/aging-report";
import { PageHeader } from "@/components/ui/page-header";

export default function ArAgingPage() {
  return (
    <div>
      <PageHeader
        title="AR Aging"
        breadcrumb="Home / Reports / Accounts Receivable / Aging"
        description="Open balance per customer, bucketed by oldest open invoice age."
      />
      <AgingReport kind="ar" statementRoute="/reports/customer-statement" />
    </div>
  );
}
