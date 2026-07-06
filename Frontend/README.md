# Fast Accounts — Frontend

Next.js 14 + TypeScript + Tailwind. Talks to the FastAPI backend at
`NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`).

## Setup

```powershell
cd Frontend
npm install
copy .env.example .env.local
# Edit .env.local if your backend is not on http://localhost:8000
npm run dev
```

Open http://localhost:3000.

## Routes shipped

**Auth** (catalog §1)
- `/login`, `/signup`, `/verify-email`, `/forgot-password`, `/reset-password`

**Shell**
- `/dashboard` — command-center dashboard with configurable widget grid (§10.9)
- `/(app)/[...slug]` — "coming soon" catch-all so unimplemented routes never 404

**Settings** (catalog §9, §12)
- `/settings/business-information` — §12.13 (GET/PUT wired)
- `/settings/lock-date` — §9.5 global lock date
- `/settings/smart` — §12.2 accordion: Others toggles + Currency & Time Zone wired, remaining 18 sections shells
- `/settings/taxes-year-end` — §12.12 year-end + tax display + GST/ADT/FED/WHT + regions
- `/settings/coa` — §9.1.1 Chart of Account tree (Category → Section → Nominal) + Nominal Account New modal (§9.1.2)
- `/settings/sections` — §9.1.4 Section Management with Up/Down reorder + Section New modal
- `/settings/journals` — §9.2.1 list with link to new-journal form
- `/settings/journals/new` — §9.2 voucher form (balanced debit/credit grid)

**RBAC + audit** (catalog §12.3 / §12.4 / §12.15)
- `/settings/users` — company users with role assignment (CompanyMembership)
- `/settings/roles` — roles with rights tree and role templates
- `/settings/user-log` — filtered audit-log viewer

**Master-data lists + create forms** (read + write paths)
- `/bank/balances` (list) + `/bank/balances/new` (create) — §4.1
- `/bank/payments` (list + drilling) + `/bank/payments/new` (header-only) — §4.2
- `/sales/customers` (list) + `/sales/customers/new` — §5.1
- `/sales/invoices` (list with drill links) + `/sales/invoices/new` (header + line grid) + `/sales/invoices/[id]` (detail) — §5.4
- `/purchases/suppliers` (list) + `/purchases/suppliers/new` — §6.1
- `/purchases/bills` (list with drill links) + `/purchases/bills/new` (header + line grid) + `/purchases/bills/[id]` (detail) — §6.3
- `/inventory/products` (list) + `/inventory/products/new` — §7.1
- `/settings/journals/new` — balanced debit/credit grid — §9.2

**Reports** (catalog §10 Financial)
- `/reports` — Reports hub landing
- `/reports/trial-balance` — aggregated debit/credit/balance per nominal with as-of-date filter, totals card, drill-through to GL
- `/reports/general-ledger` — opening + activity + closing for one nominal, URL-queryable
- `/reports/profit-and-loss` — Income − Expense classified via `CoaCategory.categoryType`
- `/reports/balance-sheet` — Assets / Liabilities / Equity + Retained Earnings with difference check

**GL spine (Sprint 1)**
- All operational documents (Sales Invoice, Supplier Bill, Bank Payment) auto-post a balanced journal when the matching default nominal codes are set in Smart Settings → "Default nominals".
- Every doc-creating route now enforces the company **Lock Date** server-side; backdated edits return a clear error.
- Set each COA category's **type** (Income / Expense / Asset / Liability / Equity / Other) inline on `/settings/coa` — drives P&L + BS classification.

**AR/AP loop (Sprint 2)**
- `/sales/receipts` (list) + `/sales/receipts/new` — customer receipt with auto DR bank / CR receivables posting (§5.8)
- `/purchases/payments` (list) + `/purchases/payments/new` — supplier payment with auto DR payables / CR bank posting (§6.4)
- `/bank/receipts` (list) + `/bank/receipts/new` — bank receipt (IR) with optional counterpart nominal (§4.3)
- `/bank/transfers` (list) + `/bank/transfers/new` — bank transfer with DR to-bank / CR from-bank posting (§4.4)
- All four enforce the lock date; all four return a `postingWarning` string the UI surfaces when defaults are missing.

**AR/AP visibility (Sprint 3)**
- `/reports/ar-aging` + `/reports/ap-aging` — open balance per party bucketed (Older / Current / 1-7 / 8-14 / 15-21 / 22-28 / Future) with totals card and drill-through to the statement.
- `/reports/customer-statement?customerId=…` + `/reports/supplier-statement?supplierId=…` — chronological invoice/receipt ledger with running balance.
- Dashboard now opens with **AR Aging** and **AP Aging** cards (total outstanding + party count + bucket strip).

**Operational documents (Sprint 4)**
- `/sales/quotations` + `/sales/quotations/new` — pre-sale quote (§5.2), no GL impact.
- `/sales/orders` + `/sales/orders/new` — sales order with status lifecycle (§5.3).
- `/sales/credits` + `/sales/credits/new` — sales credit auto-posting DR sales / CR receivables (§5.5).
- `/purchases/orders` + `/purchases/orders/new` — purchase order with status lifecycle (§6.2).
- `/purchases/credits` + `/purchases/credits/new` — supplier credit auto-posting DR payables / CR purchases (§6.3 VC).
- All five share a single reusable `LineGridForm` component; status transitions via `PUT …/status`. `StatusBadge` standardises colored chips across all lists.

**Document conversions (Sprint 5)**
- `/sales/quotations/[id]` — detail with status select + **Convert to sales order**.
- `/sales/orders/[id]` — detail with status select + **Convert to invoice** (copies lines, posts AR journal, marks SO `invoiced`).
- `/purchases/orders/[id]` — detail with status select + **Convert to bill** (copies lines, posts AP journal, marks PO `billed`).
- All three reuse a `DocumentDetail` component (header / line table / status select / convert button + posting warning).
- Backend `ConversionService` with three methods; lock-date guard enforced on every conversion.

**FIFO allocation (Sprint 6)**
- Receipt + payment create accept `autoFifo: true` (default on the UI checkbox) or explicit `allocations: [{invoiceId|billId, amount}, …]`.
- Server validates per-invoice remaining and receipt cap, then writes `SalesReceiptAllocation` / `SupplierPaymentAllocation` rows.
- AR/AP Aging now uses **per-invoice remaining**: partial receipts on a single invoice are reflected accurately; unallocated receipts subtract as customer advances.
- Backend `AllocationService` exposes both paths; routes return `allocations`, `totalAllocated`, `unallocatedBalance`.

## Layout

```
src/
  app/
    (auth)/        # public auth pages
    (app)/         # protected app shell
      [...slug]/   # coming-soon catch-all
      dashboard/
      settings/
  components/
    app/           # shell components (Sidebar, TopBar, SettingsMenu)
    ui/            # primitive UI (Button, Input, Label, Checkbox, Accordion, …)
  config/
    navigation.ts      # sidebar map — §2.1
    settings-menu.ts   # settings mega-menu — §12.1
  lib/
    api/
      client.ts    # typed fetch + JWT refresh
      auth.ts      # /auth/* + /companies/* wrappers
      tenant.ts    # /companies/{id}/* wrappers
    auth/
      storage.ts   # token + current-company localStorage
    utils.ts       # cn() helper
```

## Catalog parity guardrails

- The sidebar (`src/config/navigation.ts`) mirrors §2.1 verbatim.
- The Settings mega-menu (`src/config/settings-menu.ts`) mirrors §12.1.
- Every catalog-named screen must land at the route declared in those two files; do not invent new top-level routes without updating the catalog cross-reference.

## Related services

- Backend API must run on `:8000` (see `Backend/README.md`).
- **Settings → Migrations requires the data-ingestion service on `:4100`** — see `services/data-ingestion/README.md` and the root `ONBOARDING.md`.
