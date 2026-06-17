/** Customer Statement — catalog §5.9. */
import { StatementReport } from "@/components/app/statement-report";
import { PageHeader } from "@/components/ui/page-header";

export default function CustomerStatementPage() {
  return (
    <div>
      <PageHeader
        title="Customer Statement"
        breadcrumb="Home / Reports / Accounts Receivable / Customer Statement"
        description="Per-customer invoices and receipts with running balance. URL-queryable: ?customerId=…"
      />
      <StatementReport kind="customer" />
    </div>
  );
}
