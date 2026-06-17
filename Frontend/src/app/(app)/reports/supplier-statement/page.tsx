/** Supplier Statement — catalog §6 supplier statement. */
import { StatementReport } from "@/components/app/statement-report";
import { PageHeader } from "@/components/ui/page-header";

export default function SupplierStatementPage() {
  return (
    <div>
      <PageHeader
        title="Supplier Statement"
        breadcrumb="Home / Reports / Accounts Payable / Supplier Statement"
        description="Per-supplier bills and payments with running balance. URL-queryable: ?supplierId=…"
      />
      <StatementReport kind="supplier" />
    </div>
  );
}
