# Print & export matrix

Coverage for browser **Print / Save as PDF** (`/print/*` routes + `window.print()`) and **Export CSV** (client-side or API).

## Commercial documents (dedicated print routes)

| Document | Detail Print | Route |
|----------|--------------|-------|
| Sales invoice | Yes | `/print/sales-invoice/[id]` |
| Supplier bill | Yes | `/print/supplier-bill/[id]` |
| Quotation | Yes | `/print/quotations/[id]` |
| Sales order | Yes | `/print/sales-orders/[id]` |
| Purchase order | Yes | `/print/purchase-orders/[id]` |
| Sales credit | Yes | `/print/sales-credits/[id]` |
| Supplier credit | Yes | `/print/supplier-credits/[id]` |
| Sales receipt | Yes | `/print/sales-receipt/[id]` |
| Supplier payment | Yes | `/print/supplier-payment/[id]` |

## Money & GL

| Document | Detail Print | Route |
|----------|--------------|-------|
| Bank payment | Yes | `/print/bank-payment/[id]` |
| Bank receipt | Yes | `/print/bank-receipt/[id]` |
| Bank transfer | Yes | `/print/bank-transfer/[id]` |
| Journal voucher | Yes | `/print/journal/[id]` |
| PDC received | Yes | `/print/pdc-received/[id]` |
| PDC issued | Yes | `/print/pdc-issued/[id]` |

## Logistics & stock

| Document | Detail Print | Route |
|----------|--------------|-------|
| Delivery note | Yes | `/print/delivery-notes/[id]` |
| GRN | Yes | `/print/grn/[id]` |
| Stock adjustment | Yes | `/print/stock-adjustment/[id]` |
| Stock transfer | Yes | `/print/stock-transfer/[id]` |

## Financial & operational reports

| Report | Print | Export CSV |
|--------|-------|------------|
| Profit & Loss | In-page (`#report-print-area`) | Client CSV |
| Balance Sheet | In-page | Client CSV |
| Trial Balance | In-page | Client + grid export |
| General Ledger | In-page | Client + grid export |
| AR / AP Aging | In-page | Client + grid export |
| Customer / Supplier Statement | In-page | Client + grid export |
| Comparative P&L | In-page | Client CSV |
| Comparative P&L by category | In-page | API CSV (existing) |
| Extended catalog reports | In-page | Client CSV |

## Lists (EnterpriseGrid)

All primary transactional list pages expose **Export CSV** via `exportCsv` + `buildGridExport()` (exports filtered rows, not only the current page).

## Admin / settings (existing)

| Area | Export |
|------|--------|
| User log | Filtered audit CSV (API) |
| Roles | JSON export / import |
| Audit log presets | JSON export/import |

## Not in scope (yet)

- Server-generated PDF attachments (only browser print → Save as PDF)
- Bulk print from list selection
- `POST /reports/runs/{id}/export` wired in UI (backend exists for report runs)
- Bank reconciliation session print
- Product batch / COA tree export

## Implementation notes

- Print layout: `Frontend/src/app/print/layout.tsx` (no app shell)
- Document lines: `DocumentPrint` / `PlanningDocumentPrint`
- Vouchers: `VoucherPrint`
- Reports: `ReportExportActions` + `@media print` in `globals.css`
- Lists: `EnterpriseGrid` `exportCsv` prop + `lib/export/grid-export.ts`
