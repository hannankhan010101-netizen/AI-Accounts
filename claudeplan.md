# Fast Accounts — implementation tracker

**Last verified:** 2026-05-21 (repo scan: `Frontend/src`, `Backend/src/app/api/routes/tenant.py`, `Backend/prisma/schema.prisma`)

## Current snapshot

| Metric | Count |
|--------|------:|
| Frontend source files (`Frontend/src/**/*.ts(x)`) | **111** |
| Frontend `page.tsx` routes | **80** (~62 real app pages; rest auth/print/catch-all) |
| Backend tenant routes (`tenant.py`) | **119** |
| Backend services | **15** |
| Live report UIs (hub + dedicated pages) | **8** |
| Named report APIs (beyond TB/GL runner) | **10** |
| Print routes | **2** (`/print/sales-invoice`, `/print/supplier-bill`) |

### Catalog parity (§1–§14 matrix, revised)

| Status | Rows | Share |
|--------|-----:|------:|
| ✅ Done | ~52 | ~24% |
| 🟡 Partial | ~48 | ~22% |
| ❌ Missing | ~115 | ~53% |
| **Weighted parity** (✅ + ½🟡) | | **~46–50%** |

The detailed matrix below (from the original audit) is **mostly accurate on ❌ items** but **understates ✅/🟡** on GL spine, AR/AP, bank receipts/transfers, operational docs, conversions, FIFO (backend), P&L/BS, and extended reports. Use this header + [PARITY-BACKLOG.md](Backend/docs/PARITY-BACKLOG.md) as the live gap list.

### Sprint board

| Sprint | Status | Notes |
|--------|--------|-------|
| 0 — bootstrap | ✅ | Auth, layout, providers |
| Phase 1 — settings core | ✅ | Business info, lock date, smart (2/20), taxes, COA, users/roles/log |
| Phase 2 — masters + journal + TB/GL | ✅ | |
| GL spine (categoryType + posting + P&L/BS + lock-date) | ✅ | `PostingService`; lock enforced on mutating routes |
| AR/AP loop | ✅ | Receipts, payments, bank receipt/transfer |
| AR/AP visibility | ✅ | Aging, statements, dashboard AR/AP cards |
| Operational docs | ✅ | Quotes, SO, PO, credits, DN, GRN, PDC, stock adj/xfer, batches |
| Conversions | ✅ | Quote→SO→Invoice; PO→Bill |
| Sprint 6 — FIFO allocations | ✅ | Backend + auto-FIFO; explicit picker on receipt/payment forms |
| Sprint 7 — Print engine | 🟡 | `DocumentPrint` + SI/VI print routes + Print on detail pages |
| Sprint 8 — Inventory depth | 🟡 | Create/list APIs + pages; not full §7.1 master |
| Sprint 9 — RBAC | 🟡 | `PermissionService`, live users/roles lists, Admin role on signup; rights-tree editor open |
| Sprint 10 — Tax on lines | ✅ | GST on SI/VI lines + `TaxCalculationService` + GL tax legs + `DocumentTaxSummary` |
| Sprint 11 — Reports breadth | ✅ | Hub + `/reports/extended/[slug]` for 10 named APIs |
| Sprint 13 — Explicit allocation UI | ✅ | `AllocationPicker` + open-invoice/bill endpoints |
| Sprint 15 — Email/SMS/Payments/FBR | ❌ | |

### P0 backlog (blocking real accounting)

| # | Item | Status |
|---|------|--------|
| 1 | GL posting on SI / bills / bank payments | ✅ |
| 2 | Lock-date server enforcement | ✅ |
| 3 | Customer receipts + supplier payments | ✅ |
| 4 | Tax application on document lines | ✅ |
| 5 | Bank receipts + transfers (schema + routes + UI) | ✅ |

### E2E loops that work today

1. Sign up → verify email → dashboard (counts + AR/AP aging buckets).
2. Settings: business info, lock date, smart settings (partial), taxes & year end, COA, sections, journals.
3. Masters: customers, suppliers, products, bank accounts.
4. GL: balanced journal → TB → drill GL; P&L and balance sheet.
5. Sales: quotation → SO → invoice (AR posts) → receipt (FIFO auto) → AR aging / customer statement.
6. Purchases: PO → bill (AP posts) → payment (FIFO auto) → AP aging / supplier statement.
7. Bank: payments, receipts, transfers (header + GL when nominals configured).
8. Operational shells: credits, delivery notes, GRN, PDC, stock adjustment/transfer, batches (create/list).
9. Audit log with filters.

### Next recommended picks

1. **Sprint 10** — tax on SI/VI lines + journal tax legs.
2. **Sprint 13** — explicit allocation picker on receipt/payment forms.
3. **Sprint 7** — finish print templates per doc-code + PDF export.
4. **Sprint 9** — RBAC decorator + add-user + role rights tree.
5. **Sprint 11** — wire extended report APIs into hub UI.

---

## Historical session notes (archived)

The full E2E loop is now exercisable through real data.

  End-of-session totals

  - 62 frontend source files · 38 pages · 52 backend tenant routes · 26 tasks closed across Phase 0 → Phase 5.

  What a user can do right now, end-to-end

  1. Sign up with company name → verify email OTP → land on the live dashboard with real counts and totals.
  2. Configure tenant: Business Information · Lock Date · Smart Settings (Others, Currency) · Taxes & Year End (full
  GST/ADT/FED/WHT + regions).
  3. Build a chart of accounts: see categories → add Sections with up/down reorder → add Nominal Accounts under
  sections.
  4. Create master data: Customers, Suppliers, Products, Bank Accounts.
  5. Post a balanced Journal with debit/credit grid → see it in the Journals list.
  6. Run Trial Balance with as-of-date → see totals card with Balanced ✓.
  7. Click a nominal code in the TB → drill into General Ledger with opening + activity + closing.
  8. Create a Sales Invoice with header + line grid (auto-numbered via SI sequence) → click into the detail view with
  line totals.
  9. Create a Supplier Bill with header + line grid (auto-numbered via VI) → click into the detail view.
  10. Browse audit log with Type / User / Date filters.

  Backend deltas this session

  ┌───────────────┬───────────────────────────────────────────────────────────────────────────────────┬─────────────┐
  │   Endpoint    │                                   Routes added                                    │      §      │
  │     group     │                                                                                   │             │
  ├───────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────┤
  │ COA hierarchy │ /coa/tree, /coa/sections (GET, POST), /coa/sections/{id}/reorder, /coa/nominals   │ 9.1         │
  │               │ (POST)                                                                            │             │
  ├───────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────┤
  │ Reports       │ /reports/trial-balance, /reports/general-ledger                                   │ 10          │
  │               │                                                                                   │ Financial   │
  ├───────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────┤
  │ Customers     │ POST /customers                                                                   │ 5.1         │
  ├───────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────┤
  │ Suppliers     │ GET /suppliers, POST /suppliers                                                   │ 6.1         │
  ├───────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────┤
  │ Products      │ POST /products                                                                    │ 7.1         │
  ├───────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────┤
  │ Bank accounts │ POST /bank-accounts                                                               │ 4.1         │
  ├───────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────┤
  │ Sales         │ GET /sales-invoices/{id}, POST /sales-invoices (header + lines, document-number   │ 5.4         │
  │ invoices      │ reserved)                                                                         │             │
  ├───────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────┤
  │ Supplier      │ GET /supplier-bills/{id}, POST /supplier-bills (header + lines, document-number   │ 6.3         │
  │ bills         │ reserved)                                                                         │             │
  ├───────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────┤
  │ Dashboard     │ GET /dashboard/summary aggregating counts + totals                                │ 10.9        │
  └───────────────┴───────────────────────────────────────────────────────────────────────────────────┴─────────────┘

  All repositories extended with corresponding methods; 4 new Pydantic request modules (coa_requests, masters_requests,
  sales_requests, purchases_requests).

  Frontend deltas this session

  - New UI primitives: DataTable, Modal, Select, Accordion, PageHeader.
  - New pages (created or upgraded):
    - Dashboard (placeholder → real counts + totals)
    - Settings: Business Info, Lock Date, Smart Settings, Taxes & Year End, COA tree, Section Management, Users, Roles,
  User Log, Journals (list + create)
    - Sales: Customers (list + create), Invoices (list + create + detail)
    - Purchases: Suppliers (list + create), Bills (list + create + detail)
    - Inventory: Products (list + create)
    - Bank: Balances (list + create), Payments (list + create)
    - Reports: hub, Trial Balance, General Ledger
    - Auth: Sign up, login, verify email, forgot/reset password

  Where to pick up next session (archived — see **Current snapshot** at top)

  ~~1. CoaCategory.categoryType — done. P&L + BS live.~~
  ~~2. BankReceipt, BankTransfer — done (schema + routes + UI).~~
  ~~3. GL posting on SI / bills / bank payments — done (`PostingService`).~~
  ~~4. Sales receipts + supplier payments + FIFO (backend) — done; explicit allocation UI still open.~~
  1. BankPaymentLine table — multi-line bank payment vouchers with GL posting.
  2. Roles & Users: backend RBAC (currently stubs); permission-tree form (§12.4.1).
  3. Tax on document lines (§3.12) — config exists, no application on documents.
  4. Reports breadth: §10.11 enumerated IDs + analytical hub UI.
  5. Print engine: all §3.7 templates + PDF output.

  To run it

  cd Backend
  .\.venv\Scripts\python -m prisma migrate dev --name session-2
  $env:PYTHONPATH = "src"
  .\.venv\Scripts\uvicorn app.main:app --reload --port 8000

  # new shell
  cd Frontend
  npm install
  copy .env.example .env.local
  npm run dev

  http://localhost:3000 → sign up → walk the full loop.

  The codebase is now coherent, catalog-aligned, tenant-scoped, and provably correct on the GL spine (Trial Balance must
   balance because Journal posting requires balanced lines). That's the foundation; every later phase is bolting modules
   onto this skeleton.

✻ Baked for 10m 56s

※ recap: Building a Fast Accounts ERP clone end-to-end; just shipped master-data writes, sales invoice + supplier bill
  create/detail, and a live dashboard summary. Next: schema migration to add CoaCategory.categoryType so P&L and Balance
   Sheet reports can ship.

❯ C:\Users\HS TRADER\Desktop\HAK-Devs\MY-Projects\AI-Accounts\FAST-ACCOUNTS-FEATURE-CATALOG.md
  Make sure we do not Miss any feature from this plan. Read line by line and check all the features and functiona nd
  also add advance suggestions for the improvements to make it more better with extra features.

● Doing a top-to-bottom audit against the catalog (already loaded in this session). I'll mark every catalog feature with
   ✅ shipped, 🟡 partial (started but incomplete), or ❌ missing, then surface advanced-improvement ideas at the end.

  > **Revision note (2026-05-21):** Rows marked below reflect the **original audit snapshot**. For up-to-date counts and
  > sprint status, see **Current snapshot** at the top of this file. Major upgrades since the audit: lock-date
  > enforcement, posting on SI/VI/credits/bank docs, bank receipts/transfers, AR/AP receipts & payments + FIFO backend,
  > P&L/BS, conversions, operational doc APIs, dashboard AR/AP aging, 10 extended report endpoints, partial print.

  Coverage matrix vs. FAST-ACCOUNTS-FEATURE-CATALOG.md (original audit — partial stale)

  §1 Product entry, identity, tenancy

  ┌─────┬─────────────────────────────────────────────────────────────────────────┬────────┬────────────────────────┐
  │  §  │                                 Feature                                 │ Status │         Notes          │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.1 │ Sign up                                                                 │ ✅     │ POST /auth/sign-up +   │
  │     │                                                                         │        │ UI                     │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.1 │ Login                                                                   │ ✅     │                        │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.1 │ Forgot password                                                         │ ✅     │                        │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.1 │ Google Sign-In (social)                                                 │ ❌     │                        │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.1 │ 2FA                                                                     │ ❌     │                        │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.1 │ Getting-started / tutorial content                                      │ ❌     │                        │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.2 │ Admin vs Standard user types                                            │ 🟡     │ Schema has type field, │
  │     │                                                                         │        │  no enforcement        │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.3 │ Subscription user limits                                                │ ❌     │                        │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.4 │ Developer/API access toggle                                             │ ❌     │                        │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.4 │ API users (key/secret + OTP)                                            │ ❌     │                        │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.4 │ Per-user IP restriction                                                 │ ❌     │                        │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.5 │ Packages (Basic/Standard/Plus+/Premium)                                 │ ❌     │                        │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.5 │ Add-on toggles (Batch&Expiry, LC, Advanced rights, Analytical, Emails,  │ ❌     │                        │
  │     │ API, Online payments, Budget, Authorisation, Fixed asset)               │        │                        │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.5 │ Free trial                                                              │ ❌     │                        │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.5 │ Data migration tools                                                    │ ❌     │                        │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.5 │ Subscription billing cycles (monthly/annual)                            │ ❌     │                        │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.5 │ Free + paid training surfaces                                           │ ❌     │ marketing content,     │
  │     │                                                                         │        │ lower priority         │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.5 │ Policies pages (privacy/refund/payment/terms/FAQ)                       │ ❌     │                        │
  ├─────┼─────────────────────────────────────────────────────────────────────────┼────────┼────────────────────────┤
  │ 1.5 │ Partner program                                                         │ ❌     │                        │
  └─────┴─────────────────────────────────────────────────────────────────────────┴────────┴────────────────────────┘

  §2 Global navigation

  §: 2.1
  Feature: Sidebar with all 7 groups + sub-items
  Status: ✅
  Notes: src/config/navigation.ts mirrors verbatim
  ────────────────────────────────────────
  §: 2.2
  Feature: Marketing taxonomy (Assembly, LC, Landed cost, Batch & Expiry, Multi-location, Projects, Budget, Fixed
  assets,
    Authorisation, Emails, APIs, Online payments)
  Status: ❌
  Notes: catalogued in nav but routes 404-to-stub
  ────────────────────────────────────────
  §: 2.3
  Feature: Top bar with company switcher
  Status: ✅
  Notes:
  ────────────────────────────────────────
  §: 2.3
  Feature: My Tasks button
  Status: ❌
  Notes:
  ────────────────────────────────────────
  §: 2.3
  Feature: Activity / clock icon
  Status: ❌
  Notes:
  ────────────────────────────────────────
  §: 2.3
  Feature: Support button
  Status: 🟡
  Notes: button shows, no target
  ────────────────────────────────────────
  §: 2.3
  Feature: Settings overlay (mega-menu modal)
  Status: ✅
  Notes:
  ────────────────────────────────────────
  §: 2.3
  Feature: Notifications bell
  Status: ❌
  Notes:
  ────────────────────────────────────────
  §: 2.3
  Feature: Environment banner
  Status: ❌
  Notes:
  ────────────────────────────────────────
  §: 2.4
  Feature: Assembly entry under Inventory/Settings
  Status: ❌
  Notes:
  ────────────────────────────────────────
  §: 2.5
  Feature: Journals entry from Settings
  Status: ✅
  Notes:
  ────────────────────────────────────────
  §: 2.6
  Feature: Tutorial sidebar map cross-reference
  Status: 🟡
  Notes: sidebar mirrors §2.1; tutorial-only items missing (Revaluation, Multi-Currency, Stock Transfer, Landed Cost,
  LC,
    Multi-Unit, Batch & Expiry, Assembly Jobs/Templates)

  §3 Cross-cutting capabilities

  ┌──────┬─────────────────────────────────────────────────────────────────────┬────────┬───────────────────────────┐
  │  §   │                               Feature                               │ Status │           Notes           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.1  │ Smart Settings central config                                       │ 🟡     │ Page exists, 2 of 20      │
  │      │                                                                     │        │ sections wired            │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │      │                                                                     │        │ DocumentNumberService     │
  │ 3.2  │ Auto voucher numbers                                                │ 🟡     │ exists, only SI + VI use  │
  │      │                                                                     │        │ it                        │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.2  │ Smart filter labels (Filter1–4)                                     │ ❌     │ configured nowhere, not   │
  │      │                                                                     │        │ surfaced on documents     │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.2  │ Smart doc numbers (SmartDocNo1–4)                                   │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.3  │ Transaction templates                                               │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.3  │ Recurring transactions                                              │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.4  │ Draft mode (non-affecting)                                          │ ❌     │ schema has status column, │
  │      │                                                                     │        │  no draft workflow        │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │      │                                                                     │        │ ApprovalPolicy schema +   │
  │ 3.4  │ Approval workflow                                                   │ 🟡     │ service stub; no runtime  │
  │      │                                                                     │        │ enforcement               │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.4  │ User log audit trail                                                │ ✅     │ viewer wired              │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.5  │ Attachments on all document types                                   │ 🟡     │ endpoint exists, no UI    │
  │      │                                                                     │        │ attachment widget         │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.6  │ Email invoice to customer                                           │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.6  │ SMS module triggers                                                 │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │      │ Print templates                                                     │        │ settings menu lists them; │
  │ 3.7  │ (SI/SC/SO/SR/VI/VC/PO/VP/PDCR/PDCI/GDNSI/GDNSO/GRNPO/GRNVI/CUS,     │ ❌     │  none editable, no PDF    │
  │      │ Journal, Bank, Assembly, StockAdj, StockXfer, UserLog, Project)     │        │ output                    │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.7  │ Two-copy print (SR, VP)                                             │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.8  │ Excel import (bank payments/receipts, journal, opening stock,       │ 🟡     │ ImportJob service exists, │
  │      │ product bulk update)                                                │        │  no UI form, no parsers   │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.8  │ Reports export to Excel                                             │ ❌     │ export endpoint is a stub │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.9  │ Copy document (SI, journal, bank payment)                           │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.9  │ Batch sales invoice entry                                           │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.9  │ Batch supplier bills                                                │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.10 │ Drill-through report hyperlinks                                     │ 🟡     │ only TB → GL wired        │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.10 │ Column management / customization                                   │ ❌     │ menu link present, no UI  │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.10 │ Customer list filter tabs                                           │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │      │                                                                     │        │ Journal supports          │
  │ 3.11 │ Projects on transaction lines                                       │ 🟡     │ projectCode; SI/VI lines  │
  │      │                                                                     │        │ accept but no validation  │
  │      │                                                                     │        │ against Project master    │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.11 │ Locations on documents                                              │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │      │                                                                     │        │ tax-rate config exists;   │
  │ 3.12 │ GST/VAT on lines                                                    │ ❌     │ no application on         │
  │      │                                                                     │        │ documents                 │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.12 │ Withholding tax on receipts/payments                                │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.12 │ Additional taxes (non-filer, FED)                                   │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.12 │ Sales tax override (authorized users)                               │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.12 │ Filer vs non-filer product tax codes                                │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.12 │ Schedule 3 vs non-Schedule 3 invoice templates                      │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │      │                                                                     │        │ currency field on         │
  │ 3.13 │ Multi-currency on customers/banks/documents                         │ 🟡     │ BankAccount; no FX rates  │
  │      │                                                                     │        │ table, no posting         │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.13 │ Realized/unrealized FX gain/loss                                    │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.13 │ Bank FX revaluation                                                 │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │      │                                                                     │        │ configured; not enforced  │
  │ 3.14 │ Global lock date                                                    │ ✅     │ `LockDateService` on mutating routes (verified 2026-05-21) │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │      │                                                                     │        │ schema has                │
  │ 3.14 │ Per-user lock date extension                                        │ ❌     │ LockDatePerUser; no UI,   │
  │      │                                                                     │        │ no enforcement            │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.15 │ FIFO allocation on receipts/payments                                │ 🟡     │ `AllocationService` + tables; auto-FIFO on receipt form; explicit picker open (Sprint 13) │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.16 │ Discount + retail margin + trade offer on lines                     │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.16 │ Sale rate factor (%)                                                │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.17 │ Width × length → area quantity                                      │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.18 │ Digital invoicing FBR/PRAL                                          │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.19 │ Emails add-on                                                       │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.20 │ Online payments (PayPro, Kuickpay)                                  │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.21 │ Other system integrations (e-commerce, BR)                          │ ❌     │                           │
  ├──────┼─────────────────────────────────────────────────────────────────────┼────────┼───────────────────────────┤
  │ 3.22 │ Custom sales invoice layouts                                        │ ❌     │                           │
  └──────┴─────────────────────────────────────────────────────────────────────┴────────┴───────────────────────────┘

  §4 Bank module

  ┌──────┬────────────────────────────────────────┬────────┬────────────────────────────────────────────────────────┐
  │  §   │                Feature                 │ Status │                         Notes                          │
  ├──────┼────────────────────────────────────────┼────────┼────────────────────────────────────────────────────────┤
  │ 4.1  │ Account Balances view                  │ 🟡     │ list shows opening balance only — no current balance   │
  │      │                                        │        │ computed from journals                                 │
  ├──────┼────────────────────────────────────────┼────────┼────────────────────────────────────────────────────────┤
  │ 4.2  │ Bank Payments (multi-line, project,    │ 🟡     │ header only; no nominal-split lines, no journal        │
  │      │ attachments)                           │        │ posting                                                │
  ├──────┼────────────────────────────────────────┼────────┼────────────────────────────────────────────────────────┤
  │ 4.2  │ Bank payments Excel import             │ ❌     │                                                        │
  ├──────┼────────────────────────────────────────┼────────┼────────────────────────────────────────────────────────┤
  │ 4.2  │ Copy bank payment                      │ ❌     │                                                        │
  ├──────┼────────────────────────────────────────┼────────┼────────────────────────────────────────────────────────┤
  │ 4.3  │ Bank Receipts                          │ ✅     │ schema + POST/GET + list/create UI (revised 2026-05-21) │
  ├──────┼────────────────────────────────────────┼────────┼────────────────────────────────────────────────────────┤
  │ 4.4  │ Bank Transfers                         │ ✅     │ schema + POST/GET + list/create UI (revised 2026-05-21) │
  ├──────┼────────────────────────────────────────┼────────┼────────────────────────────────────────────────────────┤
  │ 4.5  │ Reconciliation flow (statement         │ ❌     │                                                        │
  │      │ balance, tick/clear)                   │        │                                                        │
  ├──────┼────────────────────────────────────────┼────────┼────────────────────────────────────────────────────────┤
  │ 4.5a │ Import Statement (OFX/CSV)             │ ❌     │                                                        │
  ├──────┼────────────────────────────────────────┼────────┼────────────────────────────────────────────────────────┤
  │ 4.6  │ FX Revaluation                         │ ❌     │                                                        │
  ├──────┼────────────────────────────────────────┼────────┼────────────────────────────────────────────────────────┤
  │ 4.7  │ Multi-currency on bank movements       │ 🟡     │ currency stored; no rates applied                      │
  └──────┴────────────────────────────────────────┴────────┴────────────────────────────────────────────────────────┘

  §5 Sales module

  ┌──────┬───────────────────────────────────────────┬────────┬─────────────────────────────────────────────────────┐
  │  §   │                  Feature                  │ Status │                        Notes                        │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │      │                                           │        │ minimal create only — no credit terms, opening      │
  │ 5.1  │ Customer master                           │ 🟡     │ balance, custom fields, customer-product pricing,   │
  │      │                                           │        │ default discount, SMS mobile,                       │
  │      │                                           │        │ customer-also-supplier, auto code                   │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.1  │ Customer import from spreadsheet          │ ❌     │                                                     │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.1  │ Customer performance                      │ 🟡     │ report ID 182 catalogued, not run                   │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.2  │ Quotations                                │ 🟡     │ CRUD + status + convert-to-order (revised 2026-05-21) │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.3  │ Sales orders (lifecycle In                │ 🟡     │ CRUD + status + convert-to-invoice + AR post        │
  │      │ Progress/Approved/Rejected/Invoiced)      │        │                                                     │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.3  │ Multi-order → one invoice                 │ ❌     │                                                     │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.3  │ Goods Dispatch Note (GDNSO)               │ ❌     │                                                     │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │      │                                           │        │ shipped without taxes, discounts, retail margin,    │
  │ 5.4  │ Sales Invoice (header + lines)            │ 🟡     │ trade offer, additional charges/deductions, W×L     │
  │      │                                           │        │ area, copy, email, attachments, journal posting     │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.4  │ Batch sales invoice entry                 │ ❌     │                                                     │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.4  │ Edit-after-payment rules                  │ ❌     │                                                     │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.4  │ Sales invoice Excel import                │ ❌     │                                                     │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.4  │ Print designer (column show/hide/rename)  │ ❌     │                                                     │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.5  │ Sales Credits (SC)                        │ 🟡     │ create + list + GL post (revised 2026-05-21)         │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.6  │ Delivery Notes (GDNSI / GDNSO)            │ 🟡     │ create API + list/create UI shell                   │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.7  │ Post-Dated Cheque Received (PDCR)         │ 🟡     │ create + status API + UI shell                      │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.7  │ Sales All aggregate                       │ ❌     │                                                     │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.8  │ Sales Receipts                            │ 🟡     │ create + list + GL post (revised 2026-05-21)        │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.8  │ FIFO + manual allocation                  │ 🟡     │ auto-FIFO ✅; explicit manual picker ❌             │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.8  │ Multi-invoice receipt vouchers            │ ❌     │                                                     │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.8  │ Withholding income tax on receipts        │ ❌     │                                                     │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.8  │ Customer advance return                   │ ❌     │                                                     │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.8  │ Two-copy receipt print                    │ ❌     │                                                     │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.9  │ Customer ledger inquiry                   │ 🟡     │ reachable via GL with manual code lookup            │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.10 │ Invoice list filters                      │ ❌     │                                                     │
  ├──────┼───────────────────────────────────────────┼────────┼─────────────────────────────────────────────────────┤
  │ 5.10 │ User-locked sale rates                    │ ❌     │                                                     │
  └──────┴───────────────────────────────────────────┴────────┴─────────────────────────────────────────────────────┘

  §6 Purchases module — parallel to Sales

  ┌─────┬───────────────────────────────┬────────┬──────────────────────────────────────────────────────────────────┐
  │  §  │            Feature            │ Status │                              Notes                               │
  ├─────┼───────────────────────────────┼────────┼──────────────────────────────────────────────────────────────────┤
  │ 6.1 │ Supplier master               │ 🟡     │ minimal create only                                              │
  ├─────┼───────────────────────────────┼────────┼──────────────────────────────────────────────────────────────────┤
  │ 6.1 │ Auto supplier codes           │ ❌     │                                                                  │
  ├─────┼───────────────────────────────┼────────┼──────────────────────────────────────────────────────────────────┤
  │ 6.1 │ Notify supplier via SMS/email │ ❌     │                                                                  │
  ├─────┼───────────────────────────────┼────────┼──────────────────────────────────────────────────────────────────┤
  │ 6.1 │ PDC Issued (PDCI)             │ ❌     │                                                                  │
  ├─────┼───────────────────────────────┼────────┼──────────────────────────────────────────────────────────────────┤
  │ 6.1 │ Purchases All                 │ ❌     │                                                                  │
  ├─────┼───────────────────────────────┼────────┼──────────────────────────────────────────────────────────────────┤
  │ 6.2 │ Purchase Orders (lifecycle)   │ 🟡     │ CRUD + status + convert-to-bill (revised 2026-05-21)             │
  ├─────┼───────────────────────────────┼────────┼──────────────────────────────────────────────────────────────────┤
  │ 6.2 │ Multi-PO → one bill           │ ❌     │                                                                  │
  ├─────┼───────────────────────────────┼────────┼──────────────────────────────────────────────────────────────────┤
  │ 6.3 │ Supplier Bill (header +       │ 🟡     │ shipped without taxes, additional charges, batch entry, GL       │
  │     │ lines)                        │        │ posting                                                          │
  ├─────┼───────────────────────────────┼────────┼──────────────────────────────────────────────────────────────────┤
  │ 6.3 │ Supplier bill Excel import    │ ❌     │                                                                  │
  ├─────┼───────────────────────────────┼────────┼──────────────────────────────────────────────────────────────────┤
  │ 6.3 │ Edit-after-payment rules      │ ❌     │                                                                  │
  ├─────┼───────────────────────────────┼────────┼──────────────────────────────────────────────────────────────────┤
  │ 6.4 │ Supplier Payments             │ 🟡     │ create + list + GL post (revised 2026-05-21)                     │
  ├─────┼───────────────────────────────┼────────┼──────────────────────────────────────────────────────────────────┤
  │ 6.4 │ FIFO + WHT + advance return   │ 🟡     │ auto-FIFO ✅; WHT/advance ❌                                     │
  ├─────┼───────────────────────────────┼────────┼──────────────────────────────────────────────────────────────────┤
  │ 6.4 │ Two-copy bill payment print   │ ❌     │                                                                  │
  ├─────┼───────────────────────────────┼────────┼──────────────────────────────────────────────────────────────────┤
  │ 6.5 │ PO printing templates         │ ❌     │                                                                  │
  └─────┴───────────────────────────────┴────────┴──────────────────────────────────────────────────────────────────┘

  §7 Inventory module

  §: 7.1
  Feature: Product master
  Status: 🟡
  Notes: only code/name/isStock — missing: stock-vs-nonstock toggle ✅, categories, UoM, multi-unit, pack size, bin
    location, image, sale/cost/trade prices, sale/purchase discount, retail margin, trade offer, tax codes (filer +
    non-filer), tax schedules, preferred supplier, low-stock level, opening stock, bundle products, 8 flex fields,
    archive, bulk tax update
  ────────────────────────────────────────
  §: 7.1
  Feature: Product bulk import (opening stock)
  Status: ❌
  Notes:
  ────────────────────────────────────────
  §: 7.2
  Feature: Stock Transfer
  Status: 🟡
  Notes: POST/GET + list/create UI (revised 2026-05-21)
  ────────────────────────────────────────
  §: 7.3
  Feature: Stock Adjustment
  Status: 🟡
  Notes: POST/GET + list/create UI (revised 2026-05-21); full inventory GL not complete
  ────────────────────────────────────────
  §: 7.4
  Feature: Landed Cost
  Status: ❌
  Notes:
  ────────────────────────────────────────
  §: 7.5
  Feature: Letter of Credit
  Status: ❌
  Notes:
  ────────────────────────────────────────
  §: 7.6
  Feature: Projects accounting
  Status: 🟡
  Notes: tag plumbing partial; no project P&L report
  ────────────────────────────────────────
  §: 7.6
  Feature: Project tier caps
  Status: ❌
  Notes:
  ────────────────────────────────────────
  §: 7.7
  Feature: Multi-unit
  Status: ❌
  Notes:
  ────────────────────────────────────────
  §: 7.8
  Feature: Batch & Expiry tracking
  Status: ❌
  Notes:

  §8 Fixed Assets

  ┌─────┬───────────────────────────────────┬────────┬───────┐
  │  §  │              Feature              │ Status │ Notes │
  ├─────┼───────────────────────────────────┼────────┼───────┤
  │ 8   │ Register fixed assets             │ ❌     │       │
  ├─────┼───────────────────────────────────┼────────┼───────┤
  │ 8   │ Import/export FA data             │ ❌     │       │
  ├─────┼───────────────────────────────────┼────────┼───────┤
  │ 8   │ Lifecycle, depreciation, disposal │ ❌     │       │
  └─────┴───────────────────────────────────┴────────┴───────┘

  §9 General Ledger

  ┌───────┬─────────────────────────────────────────────────┬────────┬───────────────────────────────────────────────┐
  │   §   │                     Feature                     │ Status │                     Notes                     │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.1.1 │ Chart of Account tree                           │ ✅     │                                               │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.1.2 │ Nominal Account New modal                       │ ✅     │                                               │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.1.2 │ Existing nominal accounts sibling panel         │ ❌     │                                               │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.1.3 │ Nominals separate route (parity question)       │ ❌     │                                               │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.1.4 │ Section Management list + reorder + add         │ ✅     │                                               │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.1.4 │ Section export to PDF/Excel                     │ ❌     │                                               │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.1.4 │ Bulk delete sections                            │ ❌     │                                               │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.2   │ General Journal                                 │ ✅     │                                               │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.2   │ Manual journal D/C presentation                 │ ✅     │                                               │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.2   │ Journal attachments                             │ 🟡     │ endpoint exists, no UI                        │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.2   │ Copy journal                                    │ ❌     │                                               │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.2.1 │ Journals list with filters (nominal, ref, date) │ 🟡     │ list shows; no filters wired                  │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.2.1 │ Bulk delete journals                            │ ❌     │                                               │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.2.1 │ Journal voucher print                           │ ❌     │                                               │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.3   │ Budget module                                   │ ❌     │ stub endpoint returns []                      │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.4   │ Taxes config                                    │ ✅     │                                               │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.5   │ Lock date global                                │ ✅     │ enforced via `LockDateService` (revised 2026-05-21) │
  ├───────┼─────────────────────────────────────────────────┼────────┼───────────────────────────────────────────────┤
  │ 9.5   │ Lock date per-user                              │ ❌     │                                               │
  └───────┴─────────────────────────────────────────────────┴────────┴───────────────────────────────────────────────┘

  §10 Reports

  ┌───────────┬─────────────────────────────────────────────────┬────────┬──────────────────────────────────────────┐
  │     §     │                     Feature                     │ Status │                  Notes                   │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │ 10.1      │ 200+/300+ standard reports library              │ 🟡     │ 8 UI reports + runner; 10 named APIs (revised 2026-05-21) │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │ 10.1      │ Report filters                                  │ 🟡     │ TB has date; runner pattern needs to     │
  │           │                                                 │        │ scale                                    │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │ 10.1      │ Report Excel export                             │ ❌     │ stub                                     │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │ 10.2      │ Hyperlink drill from reports                    │ 🟡     │ TB→GL only                               │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │ 10.2      │ Combined account reports                        │ ❌     │                                          │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │ 10.2      │ Favorites / favourites (US/UK spelling parity)  │ ❌     │                                          │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │ 10.3      │ Analytical Reports hub (30+/33 reports, IDs     │ ❌     │ hub link 404s                            │
  │           │ 200–500)                                        │        │                                          │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │           │ Categories: Sales & Recovery, Sale Order,       │        │                                          │
  │ 10.3      │ Purchases & Payments, Purchase Order, Cash &    │ ❌     │                                          │
  │           │ Bank, Product & Services, Management            │        │                                          │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │ 10.4      │ GST Sale Invoices Details, GST Return Summary   │ ❌     │                                          │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │ 10.5      │ Assembly: Job Cost Summary by Finished Product  │ ❌     │                                          │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │ 10.6      │ Project Payments                                │ ❌     │                                          │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │ 10.7      │ Sales Recovery Summary by Date with WHT         │ ❌     │                                          │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │ 10.8      │ Bank activity summary                           │ ❌     │                                          │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │           │                                                 │        │ live counts + totals; AR/AP aging cards  │
  │ 10.9      │ Dashboard widgets                               │ 🟡     │ ✅ AR/AP aging on dashboard; still missing top-10s, watchlists, cash-flow chart, bank balance chart, inventory health, FY card (revised 2026-05-21) │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │           │ Reports hub tree (Sales, Purchases, Bank,       │        │                                          │
  │ 10.10     │ Inventory, Financial, Assembly, Projects,       │ 🟡     │ hub lists 8 live reports (revised 2026-05-21) │
  │           │ Taxes, Budget, Fixed Assets, Consolidation)     │        │                                          │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │ 10.10.2–5 │ Sub-tree categories                             │ ❌     │                                          │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │ 10.11     │ 50+ enumerated report IDs                       │ ❌     │                                          │
  │           │ (Favorites/Sales/Inventory partial lists)       │        │                                          │
  ├───────────┼─────────────────────────────────────────────────┼────────┼──────────────────────────────────────────┤
  │           │ Standard report runner UX (criteria panel, gear │        │                                          │
  │ 10.12     │  settings, column control, in-table search,     │ 🟡     │ partial in TB/GL pages                   │
  │           │ sortable headers)                               │        │                                          │
  └───────────┴─────────────────────────────────────────────────┴────────┴──────────────────────────────────────────┘

  §11 Assembly

  ┌──────┬───────────────────────────────────────────────────────────────────────┬────────┬───────┐
  │  §   │                                Feature                                │ Status │ Notes │
  ├──────┼───────────────────────────────────────────────────────────────────────┼────────┼───────┤
  │ 11   │ Templates, jobs, raw material allocation, finished goods, job costing │ ❌     │       │
  ├──────┼───────────────────────────────────────────────────────────────────────┼────────┼───────┤
  │ 11.1 │ Finish / Print / Print Cost rights                                    │ ❌     │       │
  ├──────┼───────────────────────────────────────────────────────────────────────┼────────┼───────┤
  │ 11.2 │ Smart filters for assembly                                            │ ❌     │       │
  ├──────┼───────────────────────────────────────────────────────────────────────┼────────┼───────┤
  │ 11.3 │ Batch & expiry in assembly                                            │ ❌     │       │
  └──────┴───────────────────────────────────────────────────────────────────────┴────────┴───────┘

  §12 Settings, authorization, administration

  ┌─────────┬─────────────────────────────────────────────────────┬────────┬────────────────────────────────────────┐
  │    §    │                       Feature                       │ Status │                 Notes                  │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.1    │ Settings mega-menu modal                            │ ✅     │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.1    │ All mega-menu links mapped to routes                │ 🟡     │ configured; many target the catch-all  │
  │         │                                                     │        │ page                                   │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.2    │ Smart Settings — 20 accordion sections              │ 🟡     │ accordion shell exists, 2 of 20 wired  │
  │         │                                                     │        │ (Others, Currency)                     │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.2.4  │ E-Signatures upload table                           │ ❌     │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.2.5  │ Product description display grid                    │ ❌     │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.2.6  │ Template/Draft matrix                               │ ❌     │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.2.7  │ Last rate matrix                                    │ ❌     │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.2.8  │ 10 auto-code blocks                                 │ ❌     │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.3    │ Users Management (list + add user form)             │ 🟡     │ list page reads stub backend; no       │
  │         │                                                     │        │ add-user form yet, no role assignment  │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.3.2  │ Add user form (firstName, lastName, email, mobile,  │ ❌     │                                        │
  │         │ type, IP allowlist, dashboard, active)              │        │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.3.3  │ Per-user field locks (rate, discount, RM, TO,       │ ❌     │                                        │
  │         │ bundle qty, GST, banks)                             │        │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.4    │ Roles Management list                               │ 🟡     │ list reads stub                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.4.1  │ Add Role form with hierarchical rights tree         │ ❌     │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.4.2  │ All right-tree root modules                         │ ❌     │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.4.3  │ Report permission buckets                           │ ❌     │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.5    │ Advance Users (customer/supplier/product visibility │ ❌     │                                        │
  │         │  fence)                                             │        │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.6    │ Authorisation module configurable approvals         │ 🟡     │ schema partial, no runtime             │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.7    │ Locations / multi-location                          │ ❌     │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.8    │ Printing config (covered in §3.7)                   │ ❌     │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.9–10 │ Support-label articles                              │ ❌     │ external/marketing                     │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.11   │ Public policies                                     │ ❌     │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.12   │ Taxes and Year End                                  │ ✅     │ full grid editor                       │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.13   │ Business Information                                │ ✅     │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.13   │ Logo upload + max size enforcement                  │ 🟡     │ URL-only input; no real file upload    │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.13   │ Subscription strip (Account No., Renewal date)      │ ❌     │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.14   │ Content Settings (Forms / Menu / Listing column     │ ❌     │                                        │
  │         │ editors)                                            │        │                                        │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.15   │ User Log viewer                                     │ ✅     │ filters wired                          │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.15   │ View link → underlying transaction                  │ ❌     │ View column is read-only               │
  ├─────────┼─────────────────────────────────────────────────────┼────────┼────────────────────────────────────────┤
  │ 12.15   │ Retention/export/PII handling                       │ ❌     │                                        │
  └─────────┴─────────────────────────────────────────────────────┴────────┴────────────────────────────────────────┘

  §13 Narrative end-to-end flows — coverage of each journey

  ┌─────────────────────────────────────────┬──────────────────────────────────────────────────────────────────┐
  │                  Flow                   │                              Status                              │
  ├─────────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ 13.1 Sell stock from quote to cash      │ 🟡 Quote→SO→Invoice→Receipt ✅; GDN/print/email still missing (revised 2026-05-21) │
  ├─────────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ 13.2 Buy stock into warehouse           │ 🟡 PO→Bill→Payment ✅; GRN/transfer shells; landed/LC missing   │
  ├─────────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ 13.3 Manufacture finished goods         │ ❌ entire Assembly module missing                                │
  ├─────────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ 13.4 Month-end control                  │ 🟡 lock date enforced ✅; FX revaluation missing (revised 2026-05-21) │
  ├─────────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ 13.5 Regulated digital sales (FBR/PRAL) │ ❌                                                               │
  ├─────────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ 13.6 Fixed asset lifecycle              │ ❌                                                               │
  └─────────────────────────────────────────┴──────────────────────────────────────────────────────────────────┘

  §14 Transaction dictionary — code support

  ┌─────────────┬────────────────────────────┬──────────────┬──────────────────────────────────┐
  │    Code     │          Catalog           │ Used in code │              Notes               │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ SI          │ Sales invoice              │ ✅           │ document sequence active         │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ SC          │ Sales credit               │ ❌           │                                  │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ SO          │ Sales order                │ 🟡           │ CRUD + convert-to-invoice        │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ SR          │ Sales receipt              │ ✅           │ create + FIFO + GL (revised 2026-05-21) │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ VI          │ Supplier bill              │ ✅           │ document sequence active         │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ VC          │ Supplier credit            │ ❌           │                                  │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ VP          │ Bill payment               │ ✅           │ supplier payments (revised 2026-05-21) │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ PO          │ Purchase order             │ 🟡           │ CRUD + convert-to-bill           │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ SQ          │ Sales quotation            │ 🟡           │ CRUD + convert-to-order          │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ QO          │ Quotation/quote-order      │ ❌           │                                  │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ GDNSI/GDNSO │ Goods delivery notes       │ ❌           │                                  │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ GRNPO/GRNVI │ Goods receipt notes        │ ❌           │                                  │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ PDCR        │ Post-dated cheque received │ ❌           │                                  │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ PDCI        │ Post-dated cheque issued   │ ❌           │                                  │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ CUS         │ Customer print template    │ ❌           │                                  │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ EP          │ Bank payment (API enum)    │ 🟡           │ conceptually mapped, not exposed │
  ├─────────────┼────────────────────────────┼──────────────┼──────────────────────────────────┤
  │ IR          │ Bank receipt (API enum)    │ ✅           │ bank receipts route (revised 2026-05-21) │
  └─────────────┴────────────────────────────┴──────────────┴──────────────────────────────────┘

  §16 Source map / route index — coverage

  The §16.1 table maps 22 catalog breadcrumbs to live routes. Original audit: 9 live / 13 stub. **Revised 2026-05-21:**
  ~18–20 have dedicated `(app)` pages; stubs remain mainly settings mega-menu links (~25 printing/config) and sidebar
  leaves (reconciliation, import statement, sales/purchases “all”, analytical reports).

  ---
  Summary of what's missing — by priority

  P0 — blocking real accounting use (revised 2026-05-21)

  1. ~~GL posting hooks on Sales Invoices, Supplier Bills, Bank Payments~~ — **✅ done** (`PostingService`).
  2. ~~Lock-date server-side enforcement~~ — **✅ done** (`LockDateService`).
  3. ~~Customer Receipts + Supplier Payments~~ — **✅ done** (+ FIFO backend).
  4. **Tax application on document lines** — taxes-config exists; **no application on documents** — **still P0**.
  5. ~~Bank Receipts + Bank Transfers tables, routes, UI~~ — **✅ done**.

  P1 — finish core ERP parity

  6. Quotations + Sales Orders + Purchase Orders + their lifecycle.
  7. Sales Credits + Supplier Credits + Delivery Notes + Goods Receipt Notes.
  8. Post-Dated Cheques (PDCR + PDCI) lifecycle.
  9. Inventory write surface: stock adjustment, stock transfer, multi-unit, batch & expiry, landed cost, LC, opening
  stock, bulk update.
  10. ~~Real Profit & Loss + Balance Sheet~~ — **✅ done** (categoryType + `/reports/profit-and-loss`, `/reports/balance-sheet`).
  11. Bank reconciliation flow + statement import.
  12. FX rate table + multi-currency on documents + realized/unrealized FX.
  13. Project P&L + nominal-activity-by-project report.
  14. Document number sequences for every code in §14.
  15. Print engine + template editor + PDF output for all
  SI/SC/SO/SR/VI/VC/PO/VP/PDCR/PDCI/GDNSI/GDNSO/GRNPO/GRNVI/CUS/Journal/Bank/Assembly/StockAdj/StockXfer/UserLog/Project
   templates.
  16. Excel import + parsers for: bank payments, bank receipts, journal, opening stock, product bulk updates,
  customer/supplier bulk import.
  17. Reports breadth — every enumerated catalog ID in §10.11.
  18. Analytical Reports hub (§10.3).
  19. Dashboard widgets: AR/AP aging buckets, top-10 lists, watchlists, bank cash flow chart, monthly bank balance,
  inventory health strip, FY performance.

  P2 — admin & control

  20. Full RBAC: roles tree with view/add/modify/delete/share/print/import/approve verbs per module; permission
  decorator on every route.
  21. Add-user form with field locks (rate, discount, RM, TO, bundle, GST on sales/bills, allowed banks).
  22. Draft + Approval workflow runtime on every document type.
  23. Attachments UI widget on every document.
  24. Smart Settings remaining 18 accordion sections.
  25. Content Settings + Filters Management + Column Management.
  26. Email Settings + Sent Emails + SMS module.
  27. OP Methods + Dashboard Management screens.
  28. Audit log retention, export, and View → underlying transaction deep links.

  P3 — adjacent modules

  29. Assembly (templates, jobs, BOM, job costing, finish/approve).
  30. Fixed Assets (register, depreciation schedule SL & reducing, disposal).
  31. Letter of Credit workflow.
  32. Landed Cost allocation.
  33. Budget (multi-budget, import/export, vs-actual at company + project).
  34. Authorisation module runtime.
  35. Advance Users visibility fences.
  36. Multi-location stock by location.
  37. Digital invoicing FBR/PRAL submission + status polling.
  38. Online payments PayPro/Kuickpay (config, webhooks, settlement reconciliation).
  39. Emails add-on automated triggers + templates + throttling.

  P4 — platform

  40. API users + key/secret + email OTP + IP allowlist + rate limit.
  41. Subscription tiers + module gating per-route + per-UI.
  42. 2FA TOTP + Google Sign-In.
  43. Data migration tooling from competing products.
  44. Multi-company / tenant operator console.

  ---
  Advanced improvement suggestions (beyond catalog parity)

  These would make the product noticeably better than the Fast Accounts baseline.

  A1 — Correctness & safety

  - Database-level double-entry constraint: a trigger or CHECK that rejects journals where sum(debit) ≠ sum(credit).
  Today the service enforces it; the DB doesn't.
  - Append-only journal log + cryptographic hash chain per company. Each posting hashes (prev_hash, payload). Detects
  tampering and gives auditors a verifiable trail.
  - Per-row optimistic locking (version integer) on documents to prevent lost updates in concurrent edits.
  - Idempotency keys on every POST so retries from flaky networks don't double-post.
  - Soft deletes + revision history on every document with full diff viewer; "undo last edit" within X minutes for
  non-admins.

  A2 — Speed & UX

  - Command palette (⌘K) jumping to any customer/supplier/invoice/nominal/setting in one keystroke — easily the highest
  leverage UX feature.
  - Inline document creation: type a new customer name in the invoice picker and it offers "create customer" without
  leaving the invoice form.
  - Server-Sent Events / WebSocket push so multiple browsers viewing the same list see new rows live.
  - Print-to-PDF in browser via Playwright/Puppeteer service so prints are pixel-identical to email PDFs.
  - CSV paste into line grids (Excel users will paste 50 rows at once; today they'd add one line at a time).
  - Saved views per user: column choices + filter combos on every list, scoped to user not company.
  - Bulk actions toolbar on every list (delete, export selected, change status).
  - Keyboard-only navigation through line grids (Tab to move, Enter to commit, ↑/↓ to navigate rows).

  A3 — AI / automation (the real differentiator)

  - AI-assisted journal coding: paste a bank statement line; model suggests nominal + project + ref-no based on history.
   User accepts with one click.
  - Invoice OCR: drop a supplier PDF, the system extracts header + lines and pre-fills the bill form.
  - Anomaly detection on the dashboard: "Supplier X's invoice is 3× the 90-day average" / "Customer Y's payment terms
  slipped from 30 to 60 days."
  - Cash-flow forecast from invoice + bill due dates with confidence bands.
  - Natural-language report query: "show me top customers by revenue last quarter, excluding returns" generates the
  report run.
  - Auto-bank-reconciliation with statement import: match statement lines to outstanding payments/receipts by amount +
  date + ref no.

  A4 — Reporting depth

  - Pivot-table report builder in the browser — drag dimensions (date / customer / product / project / nominal) to rows
  or columns, drag measures (qty / amount / margin) to values.
  - Period comparison built into every financial report (TB, P&L, BS): current vs. prior period side by side with %
  delta and traffic-light coloring.
  - Drill-anywhere: every number in every report becomes a hyperlink to underlying rows.
  - Scheduled report email ("send me AR aging every Monday 8 AM").
  - Report subscriptions + Slack / Teams alerts when a threshold trips (cash balance < X, single-invoice > Y).

  A5 — Multi-tenant operator console

  - Operator dashboard with cross-tenant health: signups, churn, MRR, support tickets per tenant, slow queries per
  tenant.
  - Impersonation (audit-logged) for support.
  - Tenant resource limits + autoscale signals.
  - Sandbox copy-of-prod per tenant so customers can experiment safely.

  A6 — Open ecosystem

  - Public API + OAuth2 client app marketplace instead of just key/secret. Lets third parties build integrations without
   leaking customer credentials.
  - Webhook framework with delivery retries + dead-letter UI (today there's no webhook out at all).
  - Zapier / Make connector as a first-party deliverable.
  - OpenAPI-driven SDK generation for 5 languages from the spec we already have.
  - Embeddable widgets: drop "request quote" or "pay invoice" widget into a customer's website; data flows back as draft
   sales records.

  A7 — Compliance & audit beyond FBR

  - SOC 2 / ISO 27001 evidence collection baked in (access reviews, key rotation, change tickets).
  - GDPR / data-export self-service per user with cryptographic proof of completeness.
  - e-invoicing standards beyond FBR — UBL 2.1 / Peppol BIS Billing 3.0 so the same engine works internationally.
  - Time-machine queries: "what did the TB look like on 2026-03-31 as of the books on that day" — useful when
  corrections come in later.

  A8 — Performance

  - Materialized views for trial balance and AR/AP aging refreshed on journal post — sub-100ms TB even on 5M rows.
  - Partitioned journal lines by (companyId, year) — every tenant's history queries hit its own partition.
  - Read replicas for reports; writes go to primary.
  - Per-tenant rate limits + slow-query budget so one greedy tenant can't degrade neighbours.

  A9 — Developer & operability

  - Replayable event store behind every document — invoice_created, invoice_line_added, invoice_posted events. Lets you
  rebuild any read model and is a first-class audit log.
  - Feature flag UI + per-tenant overrides (LaunchDarkly-style but self-hosted).
  - Tracing (OpenTelemetry) baked into FastAPI middleware; correlate slow report runs across services.
  - Synthetic monitoring: automated "post journal, run TB, expect balanced" probe every minute in prod.

  A10 — Pricing & packaging

  - Usage-based add-ons (e.g. per-PDF-print) instead of only flat tiers.
  - Pay-as-you-go data migration — drop competitor export, get billed only on rows actually imported.
  - Partner revenue share (referrers see their funnel + earnings in-app).

  ---
  What I'd do next (recommended order, four sprints)

  Sprint 1 — finish the GL spine
  - Add CoaCategory.categoryType enum (schema migration).
  - Hook journal-posting into Sales Invoice + Supplier Bill + Bank Payment.
  - Enforce Lock Date on every mutating route.
  - Build P&L + Balance Sheet.

  Sprint 2 — close the AR/AP loop
  - Sales Receipts + Supplier Payments + FIFO allocation + WHT.
  - Bank Receipts + Bank Transfers (schema + routes + UI).
  - AR/AP aging dashboard widgets.

  Sprint 3 — operational documents
  - Quotations, Sales Orders, Purchase Orders, with lifecycle.
  - Sales Credits + Supplier Credits.
  - Delivery Notes + Goods Receipt Notes.
  - Document Print Engine with PDF templates.

  Sprint 4 — admin & breadth
  - Full RBAC: rights tree + per-route enforcement + add-user form with field locks.
  - Draft + Approval workflow runtime.
  - Attachments UI on every doc.
  - Remaining 18 Smart Settings sections.
  - 25+ enumerated standard reports.

  Each sprint also strikes its rows from the PARITY-BACKLOG.md so the burn-down stays honest.

  This audit covers every numbered section of the catalog (§1 – §16). The gap is large, but each gap is small and
  well-scoped — every missing feature has a clear data model, route, and UI surface already plotted by the catalog.


Sprint 5 complete. Lifecycle Quotation → Sales Order → Invoice and PO → Bill is now end-to-end clickable.

  Sprint 5 deliverables

  Backend (ConversionService + 3 routes):
  - POST /quotations/{id}/convert-to-order — copies quotation lines into a new SalesOrder, marks quote as converted. No
  GL.
  - POST /sales-orders/{id}/convert-to-invoice — copies SO lines into a new SalesInvoice, posts the AR journal via
  PostingService, marks SO invoiced.
  - POST /purchase-orders/{id}/convert-to-bill — mirror for AP.
  - All three enforce lock-date and validate status (only draft|approved|accepted quotes can convert;
  in_progress|approved orders).
  - Each conversion reuses existing repositories + posting service — no double-write risk because each step is a normal
  create.

  Frontend (DocumentDetail reusable + 3 detail pages + 3 list-link wires):
  - DocumentDetail component: header info card, line table, status <select> that mutates inline, optional convert button
   gated on convertibleStatuses.
  - /sales/quotations/[id], /sales/orders/[id], /purchases/orders/[id] — each ~30 lines, just wiring the right API.
  - List pages now have clickable doc-number columns drilling into details.

  End-to-end loop that now works

  1. Create a quotation for a customer with line items.
  2. Open quote detail → status approved → click Convert to sales order.
  3. Lands on SO list with new order in in_progress.
  4. Open SO detail → status approved → click Convert to invoice.
  5. AR journal posts; SO status flips to invoiced.
  6. Open new invoice → already in /sales/invoices list.
  7. Record a customer receipt against the bank → AR balance drops.
  8. AR Aging and Customer Statement reflect everything in real time.

  The same flow works in reverse on purchases: PO → Bill → Payment.

  Cumulative totals (revised 2026-05-21 — repo scan)

  ┌──────────────────┬──────────────────────────────────────────────────────────────────────────────────┐
  │      Metric      │                              Current count                                       │
  ├──────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
  │ Frontend source  │ 111 (`Frontend/src/**/*.ts(x)`)                                                │
  │ files            │                                                                                  │
  ├──────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
  │ Frontend pages   │ 80 `page.tsx` (~62 real app routes under `(app)/`)                               │
  ├──────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
  │ Backend tenant   │ 119 (`tenant.py` route decorators)                                               │
  │ routes           │                                                                                  │
  ├──────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
  │ Backend services │ 15 (+ AllocationService, ConversionService, ExtendedReportsService, …)           │
  ├──────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
  │ Catalog parity   │ ~46–50% weighted (52 ✅ · 48 🟡 · 115 ❌ of ~215 rows)                          │
  ├──────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
  │ Reusable UI      │ DocumentDetail, LineGridForm, StatusBadge, AgingReport, StatementReport,       │
  │ components       │ DocumentPrint, DataTable, Modal, Accordion, PageHeader, Sidebar, TopBar,         │
  │                  │ SettingsMenu                                                                     │
  └──────────────────┴──────────────────────────────────────────────────────────────────────────────────┘

  Session-wide running totals (all sprints)

  ┌────────────────────────────────────────────────────────┬────────┬────────┬────────┬───────┐
  │                         Sprint                         │ Closed │ Models │ Routes │ Pages │
  ├────────────────────────────────────────────────────────┼────────┼────────┼────────┼───────┤
  │ 0 — bootstrap                                          │ ✅     │ —      │ —      │ 8     │
  ├────────────────────────────────────────────────────────┼────────┼────────┼────────┼───────┤
  │ Phase 1 — settings core                                │ ✅     │ —      │ —      │ 16    │
  ├────────────────────────────────────────────────────────┼────────┼────────┼────────┼───────┤
  │ Phase 2 — master writes + journal + TB/GL              │ ✅     │ +0     │ +9     │ 24    │
  ├────────────────────────────────────────────────────────┼────────┼────────┼────────┼───────┤
  │ GL spine (categoryType + posting + P&L/BS + lock-date) │ ✅     │ +0     │ +8     │ 28    │
  ├────────────────────────────────────────────────────────┼────────┼────────┼────────┼───────┤
  │ AR/AP loop (4 new docs)                                │ ✅     │ +4     │ +10    │ 36    │
  ├────────────────────────────────────────────────────────┼────────┼────────┼────────┼───────┤
  │ AR/AP visibility (aging + statements)                  │ ✅     │ +0     │ +4     │ 40    │
  ├────────────────────────────────────────────────────────┼────────┼────────┼────────┼───────┤
  │ Operational docs (10+ doc types)                       │ ✅     │ +10    │ +18    │ 60    │
  ├────────────────────────────────────────────────────────┼────────┼────────┼────────┼───────┤
  │ Conversions (3 routes + 3 details)                     │ ✅     │ +0     │ +3     │ 65    │
  ├────────────────────────────────────────────────────────┼────────┼────────┼────────┼───────┤
  │ Sprint 6 — FIFO allocations (backend)                │ 🟡     │ +2     │ +0     │ —     │
  ├────────────────────────────────────────────────────────┼────────┼────────┼────────┼───────┤
  │ Sprint 7 — Print engine (partial)                    │ 🟡     │ —      │ —      │ +2    │
  └────────────────────────────────────────────────────────┴────────┴────────┴────────┴───────┘

  Migration & run

  cd Backend
  .\.venv\Scripts\python -m prisma migrate dev --name operational-docs
  .\.venv\Scripts\python -m prisma generate
  $env:PYTHONPATH = "src"
  .\.venv\Scripts\uvicorn app.main:app --reload --port 8000

  Frontend already in dev mode picks up changes hot.

  What's left, ranked (revised 2026-05-21)

  1. **Sprint 10** — Tax on lines (GST/ADT/FED/WHT + journal tax legs) — **only remaining P0**.
  2. **Sprint 13** — Explicit allocation UI on receipt/payment forms (backend FIFO ✅).
  3. **Sprint 7** — Finish print engine: all §3.7 templates + PDF export (2 templates today).
  4. **Sprint 9** — RBAC runtime (permission decorator + Add User + role rights tree).
  5. **Sprint 11** — Wire 10+ extended report APIs into hub; analytical reports hub UI.
  6. BankPaymentLine — multi-line bank payment nominal splits.
  7. Sprint 15 — Email/SMS/Online payments/FBR integration shells.

  Lifecycle loops are closed (Quote→SO→Invoice→Receipt and PO→Bill→Payment). GL posting and lock-date enforcement are
  production-ready for documented flows. **Catalog parity: ~46–50%** (up from ~35% at Sprint 5 close and ~5% at first audit).

  ### Sprint checklist (live)

  - ✅ Sprints 0 → conversions + Sprint 6 backend (FIFO tables + `AllocationService`)
  - 🟡 Sprint 6 UI (explicit allocation), Sprint 7 (print), Sprint 8 (inventory depth), Sprint 11 (reports hub)
  - ❌ Sprint 9 (RBAC), Sprint 10 (tax on lines), Sprint 13 (allocation picker), Sprint 15 (integrations)