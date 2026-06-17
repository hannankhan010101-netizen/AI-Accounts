"""Content Settings listing targets — catalog §12.14."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ListingColumnDef:
    key: str
    label: str
    active: bool = True


@dataclass(frozen=True, slots=True)
class ListingDef:
    id: str
    label: str
    branch: str
    columns: tuple[ListingColumnDef, ...]


LISTING_CATALOG: tuple[ListingDef, ...] = (
  ListingDef(
      "sales-invoice",
      "Sale invoice listing",
      "Sales Listing",
      (
          ListingColumnDef("documentNumber", "Doc no."),
          ListingColumnDef("invoiceDate", "Date"),
          ListingColumnDef("customerId", "Customer"),
          ListingColumnDef("totalAmount", "Amount"),
          ListingColumnDef("status", "Status"),
      ),
  ),
  ListingDef(
      "sales-receipt",
      "Sale receipts listing",
      "Sales Listing",
      (
          ListingColumnDef("receiptNumber", "Doc no."),
          ListingColumnDef("receiptDate", "Date"),
          ListingColumnDef("customerId", "Customer"),
          ListingColumnDef("totalAmount", "Amount"),
          ListingColumnDef("unallocatedBalance", "Balance"),
          ListingColumnDef("journalId", "Posted"),
      ),
  ),
  ListingDef(
      "sales-order",
      "Sale orders listing",
      "Sales Listing",
      (
          ListingColumnDef("orderNumber", "Doc no."),
          ListingColumnDef("orderDate", "Date"),
          ListingColumnDef("customerId", "Customer"),
          ListingColumnDef("totalAmount", "Amount"),
          ListingColumnDef("status", "Status"),
      ),
  ),
  ListingDef(
      "quotation",
      "Quotation listing",
      "Sales Listing",
      (
          ListingColumnDef("quotationNumber", "Doc no."),
          ListingColumnDef("quotationDate", "Date"),
          ListingColumnDef("customerId", "Customer"),
          ListingColumnDef("totalAmount", "Amount"),
          ListingColumnDef("status", "Status"),
      ),
  ),
  ListingDef(
      "delivery-note",
      "Delivery note listing",
      "Sales Listing",
      (
          ListingColumnDef("voucherNumber", "Doc no."),
          ListingColumnDef("deliveryDate", "Date"),
          ListingColumnDef("customerId", "Customer"),
          ListingColumnDef("status", "Status"),
      ),
  ),
  ListingDef(
      "pdc-received",
      "Post dated cheque received listing",
      "Sales Listing",
      (
          ListingColumnDef("voucherNumber", "Doc no."),
          ListingColumnDef("chequeNumber", "Cheque no."),
          ListingColumnDef("chequeDate", "Cheque date"),
          ListingColumnDef("customerId", "Customer"),
          ListingColumnDef("amount", "Amount"),
          ListingColumnDef("status", "Status"),
      ),
  ),
  ListingDef(
      "pdc-issued",
      "Post dated cheque issued listing",
      "Purchase Listing",
      (
          ListingColumnDef("voucherNumber", "Doc no."),
          ListingColumnDef("chequeNumber", "Cheque no."),
          ListingColumnDef("chequeDate", "Cheque date"),
          ListingColumnDef("supplierId", "Supplier"),
          ListingColumnDef("amount", "Amount"),
          ListingColumnDef("status", "Status"),
      ),
  ),
  ListingDef(
      "customers",
      "Customers listing",
      "Sales Listing",
      (
          ListingColumnDef("code", "Code"),
          ListingColumnDef("name", "Name"),
          ListingColumnDef("phone", "Phone"),
          ListingColumnDef("email", "Email"),
          ListingColumnDef("creditLimit", "Credit limit"),
      ),
  ),
  ListingDef(
      "suppliers",
      "Suppliers listing",
      "Purchase Listing",
      (
          ListingColumnDef("code", "Code"),
          ListingColumnDef("name", "Name"),
          ListingColumnDef("email", "Email"),
          ListingColumnDef("phone", "Phone"),
      ),
  ),
  ListingDef(
      "advanced-sales-invoice",
      "Advanced sale invoice listing",
      "Sales Listing",
      (
          ListingColumnDef("documentNumber", "Doc no."),
          ListingColumnDef("invoiceDate", "Date"),
          ListingColumnDef("customerId", "Customer"),
          ListingColumnDef("projectId", "Project"),
          ListingColumnDef("totalAmount", "Amount"),
          ListingColumnDef("status", "Status"),
      ),
  ),
  ListingDef(
      "supplier-bill",
      "Supplier bill listing",
      "Purchase Listing",
      (
          ListingColumnDef("documentNumber", "Doc no."),
          ListingColumnDef("billDate", "Date"),
          ListingColumnDef("supplierId", "Supplier"),
          ListingColumnDef("totalAmount", "Amount"),
          ListingColumnDef("status", "Status"),
      ),
  ),
  ListingDef(
      "supplier-payment",
      "Bill payments listing",
      "Purchase Listing",
      (
          ListingColumnDef("voucherNumber", "Doc no."),
          ListingColumnDef("paymentDate", "Date"),
          ListingColumnDef("supplierId", "Supplier"),
          ListingColumnDef("totalAmount", "Amount"),
          ListingColumnDef("unallocatedBalance", "Balance"),
          ListingColumnDef("journalId", "Posted"),
      ),
  ),
  ListingDef(
      "purchase-order",
      "Purchase orders listing",
      "Purchase Listing",
      (
          ListingColumnDef("orderNumber", "Doc no."),
          ListingColumnDef("orderDate", "Date"),
          ListingColumnDef("supplierId", "Supplier"),
          ListingColumnDef("totalAmount", "Amount"),
          ListingColumnDef("status", "Status"),
      ),
  ),
  ListingDef(
      "grn",
      "Goods received listing",
      "Purchase Listing",
      (
          ListingColumnDef("voucherNumber", "Doc no."),
          ListingColumnDef("receiptDate", "Date"),
          ListingColumnDef("supplierId", "Supplier"),
          ListingColumnDef("sourceKind", "Source"),
          ListingColumnDef("status", "Status"),
      ),
  ),
  ListingDef(
      "supplier-credit",
      "Supplier credit listing",
      "Purchase Listing",
      (
          ListingColumnDef("creditNumber", "Doc no."),
          ListingColumnDef("creditDate", "Date"),
          ListingColumnDef("supplierId", "Supplier"),
          ListingColumnDef("totalAmount", "Amount"),
          ListingColumnDef("status", "Status"),
      ),
  ),
  ListingDef(
      "sales-credit",
      "Sale credit listing",
      "Sales Listing",
      (
          ListingColumnDef("creditNumber", "Doc no."),
          ListingColumnDef("creditDate", "Date"),
          ListingColumnDef("customerId", "Customer"),
          ListingColumnDef("totalAmount", "Amount"),
          ListingColumnDef("status", "Status"),
          ListingColumnDef("journalId", "Posted"),
      ),
  ),
  ListingDef(
      "bank-transfer",
      "Bank transfer listing",
      "Bank Listing",
      (
          ListingColumnDef("voucherNumber", "Doc no."),
          ListingColumnDef("transferDate", "Date"),
          ListingColumnDef("fromBankAccountId", "From account"),
          ListingColumnDef("toBankAccountId", "To account"),
          ListingColumnDef("totalAmount", "Amount"),
      ),
  ),
  ListingDef(
      "products",
      "Product listing",
      "Inventory Listing",
      (
          ListingColumnDef("code", "Code"),
          ListingColumnDef("name", "Name"),
          ListingColumnDef("type", "Type"),
          ListingColumnDef("category", "Category"),
          ListingColumnDef("unit", "Unit"),
          ListingColumnDef("cost", "Cost"),
      ),
  ),
  ListingDef(
      "sales-all",
      "All sales activity listing",
      "Sales Listing",
      (
          ListingColumnDef("docType", "Type"),
          ListingColumnDef("documentNumber", "Doc no."),
          ListingColumnDef("documentDate", "Date"),
          ListingColumnDef("partyId", "Customer"),
          ListingColumnDef("totalAmount", "Amount"),
          ListingColumnDef("status", "Status"),
      ),
  ),
  ListingDef(
      "purchases-all",
      "All purchase activity listing",
      "Purchase Listing",
      (
          ListingColumnDef("docType", "Type"),
          ListingColumnDef("documentNumber", "Doc no."),
          ListingColumnDef("documentDate", "Date"),
          ListingColumnDef("partyId", "Supplier"),
          ListingColumnDef("totalAmount", "Amount"),
          ListingColumnDef("status", "Status"),
      ),
  ),
  ListingDef(
      "bank-payments",
      "Bank payments listing",
      "Bank Listing",
      (
          ListingColumnDef("voucherNumber", "Doc no."),
          ListingColumnDef("paymentDate", "Date"),
          ListingColumnDef("bankAccountId", "Bank account"),
          ListingColumnDef("totalAmount", "Amount"),
      ),
  ),
  ListingDef(
      "bank-receipts",
      "Bank receipts listing",
      "Bank Listing",
      (
          ListingColumnDef("voucherNumber", "Doc no."),
          ListingColumnDef("receiptDate", "Date"),
          ListingColumnDef("bankAccountId", "Bank account"),
          ListingColumnDef("totalAmount", "Amount"),
      ),
  ),
  ListingDef(
      "journals",
      "Journals listing",
      "Accounting Listing",
      (
          ListingColumnDef("journalNumber", "Journal ID"),
          ListingColumnDef("journalDate", "Date"),
          ListingColumnDef("refNo", "Reference"),
          ListingColumnDef("totalAmount", "Total"),
      ),
  ),
  ListingDef(
      "recurring-schedules",
      "Recurring schedules listing",
      "Settings Listing",
      (
          ListingColumnDef("name", "Name"),
          ListingColumnDef("module", "Module"),
          ListingColumnDef("frequency", "Frequency"),
          ListingColumnDef("nextRunDate", "Next run"),
          ListingColumnDef("isActive", "Active"),
      ),
  ),
  ListingDef(
      "stock-adjustment",
      "Stock adjustment listing",
      "Inventory Listing",
      (
          ListingColumnDef("voucherNumber", "Voucher"),
          ListingColumnDef("adjustmentDate", "Date"),
          ListingColumnDef("reason", "Reason"),
          ListingColumnDef("status", "Status"),
          ListingColumnDef("lineCount", "Lines"),
      ),
  ),
  ListingDef(
      "stock-transfer",
      "Stock transfer listing",
      "Inventory Listing",
      (
          ListingColumnDef("voucherNumber", "Voucher"),
          ListingColumnDef("transferDate", "Date"),
          ListingColumnDef("fromLocationCode", "From"),
          ListingColumnDef("toLocationCode", "To"),
          ListingColumnDef("lineCount", "Lines"),
      ),
  ),
  ListingDef(
      "product-batches",
      "Product batches listing",
      "Inventory Listing",
      (
          ListingColumnDef("productCode", "Product"),
          ListingColumnDef("batchNumber", "Batch"),
          ListingColumnDef("expiryDate", "Expiry"),
          ListingColumnDef("quantityOnHand", "On hand"),
          ListingColumnDef("notes", "Notes"),
      ),
  ),
  ListingDef(
      "assembly-jobs",
      "Assembly jobs listing",
      "Inventory Listing",
      (
          ListingColumnDef("jobNumber", "Job no."),
          ListingColumnDef("jobDate", "Date"),
          ListingColumnDef("finishedProductCode", "Product"),
          ListingColumnDef("quantity", "Qty"),
          ListingColumnDef("status", "Status"),
      ),
  ),
  ListingDef(
      "user-log",
      "User log listing",
      "Settings Listing",
      (
          ListingColumnDef("timestamp", "Timestamp"),
          ListingColumnDef("transactionType", "Transaction type"),
          ListingColumnDef("transactionId", "Transaction ID"),
          ListingColumnDef("status", "Status"),
          ListingColumnDef("details", "Details"),
          ListingColumnDef("userName", "User"),
      ),
  ),
  ListingDef(
      "assembly-templates",
      "Assembly templates listing",
      "Inventory Listing",
      (
          ListingColumnDef("code", "Code"),
          ListingColumnDef("name", "Name"),
          ListingColumnDef("finishedProductCode", "Finished product"),
          ListingColumnDef("lines", "Components"),
      ),
  ),
  ListingDef(
      "project-payments",
      "Project payments listing",
      "Project Listing",
      (
          ListingColumnDef("voucherNumber", "Doc no."),
          ListingColumnDef("paymentDate", "Date"),
          ListingColumnDef("projectId", "Project"),
          ListingColumnDef("totalAmount", "Amount"),
      ),
  ),
)

LISTING_BY_ID: dict[str, ListingDef] = {l.id: l for l in LISTING_CATALOG}


def default_listing_layout(listing_id: str) -> dict[str, object]:
    row = LISTING_BY_ID.get(listing_id)
    if row is None:
        return {"listingId": listing_id, "columns": []}
    return {
        "listingId": listing_id,
        "columns": [
            {"key": c.key, "label": c.label, "active": c.active, "order": i}
            for i, c in enumerate(row.columns)
        ],
    }
