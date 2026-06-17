# AI-Accounts ↔ FastAccounts — Done & Remaining

**Last updated:** 2026-05-29  
**Tenant (HAK / Nafy-Pharma data):** `cmpfm1nst0001lhq3rz09938z`  
**Authority:** [FA-FULL-PARITY-IMPLEMENTATION-PLAN.md](./FA-FULL-PARITY-IMPLEMENTATION-PLAN.md), [FAST-ACCOUNTS-FEATURE-CATALOG.md](../../FAST-ACCOUNTS-FEATURE-CATALOG.md)  
**Migration detail:** [../scripts/fastaccounts_migrate/MIGRATION-AUDIT.md](../scripts/fastaccounts_migrate/MIGRATION-AUDIT.md)

---

## Executive summary

| Layer | Status | Notes |
|-------|--------|-------|
| **Navigation & pages** | ✅ Strong | 0 stub routes; FA §2.1 sidebar + settings mega-menu wired |
| **Core daily ops (SI/VI/SR/VP/bank/GRN)** | ✅ Usable | CRUD, posting, void/copy, tax legs, permissions on many mutators |
| **Reports (backend)** | ✅ Strong | 84/84 definitions have handlers; 59/59 catalog IDs mapped |
| **Reports (UI)** | ✅ Strong | 59 shortcuts + FA modules tree + full catalog with Dedicated/Runner badges |
| **Smart Settings** | ⚠️ Partial | Credit limit (SI approve), round-off on taxed lines, SR/VP/bank/SI/VI smart filters |
| **FA add-on modules** | ❌ Missing | Fixed assets, landed cost, LC, consolidation (unless licensed later) |
| **Integrations (prod)** | ✅ Env-gated | FBR/PRAL + PayPro/Kuickpay stub/live; readiness checklist UI |
| **Data migration** | ✅ Core docs | Masters + transactional counts reconciled; **GO** sign-off 2026-05-29 |
| **Deploy preflight** | ✅ | Smart Settings nominals + 5 banks for Nafy tenant |
| **DB schema apply** | ✅ `scripts/migrate_deploy.py` + drift fixes `20260529130000` / `20260529130100` |

**Definition of “100% parity”:** Full FA catalog parity requires all 115 matrix rows ✅ — **16 licensed add-ons remain ❌** (86.1% catalog). **Nafy-Pharma in-scope parity is DONE (99/99, 100%)** — see `Backend/config/nafy_parity_exclusions.json` and `PARITY-PROGRESS-LATEST.md`.

### Official signals (auto-generated)

| Gate | Status | Artifact |
|------|--------|----------|
| **Nafy go-live** | **GO** | [`GO-LIVE-SIGNOFF-LATEST.md`](./GO-LIVE-SIGNOFF-LATEST.md) |
| **Nafy in-scope parity** | **DONE (99/99)** | [`NAFY-IN-SCOPE-SIGNOFF-LATEST.md`](./NAFY-IN-SCOPE-SIGNOFF-LATEST.md) |
| **Human UAT** | **Pending** | [`NAFY-UAT-CHECKLIST.md`](./NAFY-UAT-CHECKLIST.md) · record via `scripts/record-uat-signoff.ps1` |
| **Release readiness** | Pre-deploy **READY** | [`NAFY-RELEASE-READINESS-LATEST.md`](./NAFY-RELEASE-READINESS-LATEST.md) · `scripts/nafy-release-readiness.ps1` |
| **Full FA catalog parity (every feature E2E)** | **NOT DONE** (~86% matrix ✅) | [`PARITY-PROGRESS-LATEST.md`](./PARITY-PROGRESS-LATEST.md) |

Regenerate: `python scripts/_parity_progress.py` (after `_generate_feature_matrix.py`).

---

## Automated verification (last known)

| Gate | Result | When |
|------|--------|------|
| `_route_audit.py` | 38/38 nav + 56/56 settings + 29/29 report shortcuts — **0 stubs** | 2026-05-24 |
| `_parity_audit.py` | 24/24 FA §2.1 sidebar routes | 2026-05-24 |
| `_deep_audit_reports.py` | 84/84 handlers; **0** unmapped catalog IDs | 2026-05-24 |
| Frontend `tsc --noEmit` | Pass | 2026-05-29 |
| GitHub Actions CI | pytest, typecheck, lint, build, Docker, E2E smoke | 2026-05-29 |
| Backend pytest (activity, smart settings, tax round-off) | 7 passed | 2026-05-29 |
| `e2e/parity/smoke.spec.ts` | Login + route smoke | 2026-05-29 |
| `e2e/auth.setup.ts` + `parity/authenticated.spec.ts` | Authenticated UAT (PLAYWRIGHT_AUTH_READY) | 2026-05-29 |
| `_go_live_check.py` → `GO-LIVE-SIGNOFF-LATEST.md` | Auto sign-off artifact | 2026-05-30 |
| `_report_spot_check.py` | **PASS** (16 priority reports) | 2026-05-30 |
| `_reconcile.py` (export vs DB) | **Pass** SI/SR/bills/VP counts (2026-05-29); journals extra in DB vs export | 2026-05-29 |
| `_tb_spot_check.py` | **Pass** total debit = total credit (7570 posted JEs) | 2026-05-29 |
| `_ar_ap_spot_check.py` | Run after supplemental import — compares aging vs FA snapshot | — |

Re-run:

```powershell
cd scripts
python _route_audit.py
python _deep_audit_reports.py
cd fastaccounts_migrate
python _reconcile.py
```

---

## What is done

### A. Product shell & navigation

- All FA §2.1 sidebar modules have real pages (sales, purchases, bank, inventory, reports).
- Settings §12.1 mega-menu wired (printing matrix, COA, users/roles, taxes, content, etc.).
- Command palette, EnterpriseGrid, document workspaces, print routes for major doc types.
- Dashboard widgets API + home layout gating.

### B. Phase 1 — Pharmacy daily ops (largely complete)

| # | Deliverable | Status |
|---|-------------|--------|
| 1.1 | Sales All / Purchases All — date, party, type & status filters (server + UI) | ✅ |
| 1.2 | ADT/FED on VI; WHT on SR/VP; tax config UI | ✅ |
| 1.3 | Bank reconciliation — persist `reconciledAt` / session | ✅ tick/clear/auto-match/complete |
| 1.4 | Bank receipt Excel import | ✅ |
| 1.5 | COA nominal PATCH/move; bulk delete unused nominals | ✅ |
| 1.6 | Per-user lock date UI + API | ✅ |
| 1.7 | Attachments on bank + journals | ✅ bank payment/receipt/transfer + journal detail pages |
| 1.8 | Authorisation runtime on post routes | ✅ threshold policies + guard on bank/SR/VP + SI/VI approve |
| 1.9 | PDC bounce + GL reversal | ✅ |
| 1.10 | Copy SI / bank payment / journal | ✅ |

### C. Phase 2 — Settings, listing, permissions (partial)

| # | Deliverable | Status |
|---|-------------|--------|
| 2.1 | Smart Settings — last rate (SI/VI/SO/PO/QO + view hints) | ✅ |
| 2.2 | Smart Filter labels on SI/VI/SR/VP/bank forms | ✅ |
| 2.3–2.6 | Auto-codes, e-signatures, product columns, template matrices | ⚠️ Auto-codes API wired; runtime credit limit on SI approve |
| 2.7 | Content Settings — Forms / Menu / Listing hub | ✅ |
| 2.8 | Listing catalog from API; `useConfiguredListColumns` on lists | ✅ (59 listing IDs) |
| 2.9 | Dashboard management ↔ live widgets | ✅ |
| 2.10 | OP Methods — FA option map | ✅ enabled methods + default |
| 2.11 | User log listing + presets | ✅ View links for docs, bank, journals, import jobs, parties |
| 2.12 | Expanded permission catalog + `require_permission` on mutators | ✅ |

**Listing catalog IDs wired include:** `sales-all`, `purchases-all`, `journals`, `recurring-schedules`, `stock-adjustment`, `stock-transfer`, `product-batches`, `assembly-jobs`, `assembly-templates`, `user-log`, plus standard SI/VI/bank/customer/supplier lists.

### D. Phase 3 — Documents & scheduling (partial)

| # | Deliverable | Status |
|---|-------------|--------|
| 3.1 | Transaction templates (save/load) | ✅ SI/VI/bank payment/receipt/journal |
| 3.2 | Recurring scheduler (beyond missed) | ✅ CRUD + run-due API + settings UI |
| 3.3 | Batch sales invoices screen | ✅ `/sales/invoices/batch` |
| 3.4 | Batch supplier bills screen | ✅ `/purchases/bills/batch` |
| 3.5 | Two-copy print SR/VP | ✅ `?copies=2` + template `twoCopies` |
| 3.6–3.7 | Customer/supplier advance return | ⚠️ Routes exist — verify FA parity |
| 3.8 | Batch/expiry on goods issue lines | ✅ Schema + posting tests |

### E. Phase 4 — Reports (partial)

| # | Deliverable | Status |
|---|-------------|--------|
| 4.1 | Full §10 report IDs in `report_definitions.py` | ✅ 84 rows |
| 4.2 | Reports hub — full FA tree UI | ✅ Shortcuts + **All reports** tab (API definitions) + `/reports/catalog` |
| 4.3 | Every ID → handler or “not licensed” | ✅ Handlers; UI coverage varies |
| 4.4 | Analytical hub + favorites | ⚠️ Generic runner; favorites ✅ server sync |
| 4.5 | Report criteria (status, party, product, dates) | ✅ Backend + `ReportCriteriaFields` |
| 4.6 | Server export in UI (`POST /reports/export`, runs) | ⚠️ + AR/AP aging + customer/supplier statements PDF |
| 4.7 | Hyperlinked drill-down | ⚠️ TB→GL, P&L/BS nominals→GL, GL→journal, statements→docs, dynamic grid |
| 4.8 | Budget vs actual reports | ✅ `/reports/budget-vs-actual` + `BUDGET_VS_ACTUAL` handler |
| 4.9 | Server-side PDF pipeline | ⚠️ PDF via sync export; not all report pages |

**Dedicated pages with server PDF:** trial balance, P&L, balance sheet, general ledger, customer/supplier statements (034/054), AR/AP aging (AR_AGING/AP_AGING), extended `[slug]`, comparative P&L (209/207), generic `/reports/run/[reportId]`.

### F. GL, tax, bank, sales, purchases (core APIs)

- Balanced posting on SI, VI, SR, VP, bank payments/receipts/transfers, journals (with default nominals).
- GST on lines; ADT/FED/WHT where implemented in Phase 1.2.
- FIFO allocation + explicit allocation UI on receipts/payments.
- Quotations, SO, PO, credits, GRN, delivery notes, goods issue, assembly templates/jobs (batch/expiry on finish).
- Product multi-UOM UI at `/inventory/products/[id]`.
- Customer balances report (047) and supplier balances (067) at `/reports/extended/*`.
- Bank receipts/transfers/activity + assembly templates/WIP/component extended reports.
- Smart Settings: all 20 accordions persist; runtime enforces credit limit (SI + SO), round-off, template/draft, product description defaults, auto codes, last rate API, **set customer as supplier** on create.
- Role editor: FA-style collapsible permission tree with search and per-module select/clear.
- Reports hub: **Shortcuts** (59 pinned routes), **FA modules** (standard defs by Bank/Financial/Budget/Assembly/…), **All reports** (full catalog + analytical link).
- AR/AP aging, customer/supplier statements, trial balance, P&L, balance sheet, general ledger.
- FBR submit queue (stub + PRAL live); PayPro/Kuickpay checkout + webhook with env-gated live mode.
- Roles CRUD, invite, import/export, permission-gated UI.

### G. Data migration (FastAccounts → AI-Accounts)

**Source:** `scripts/fastaccounts_export/output/fastaccounts_labeled_data.json` (39,684 records, 28 sections).

| Entity | Export → DB (2026-05-23) |
|--------|---------------------------|
| Customers | 220 ✓ |
| Suppliers | 91 ✓ |
| Products | 1,100 ✓ |
| Bank accounts | 5 ✓ |
| COA nominals | 223 ✓ |
| Sales invoices | 6,926 ✓ |
| Sales receipts | 10,260 ✓ |
| Sales credits | 78 ✓ |
| Supplier bills | 706 ✓ (incl. 18 orphan backfill) |
| Supplier payments | 960 ✓ |
| Bank payments | 1,500 ✓ |
| Journals | 2 ✓ (export only had 2) |

**Post-migration scripts run:**

- `migrate_posting_fast.py` — GL link for posted SI/bills  
- `migrate_supplemental.py` — opening stock batches, AR/AP snapshots in smart_settings  
- Orphan bills fix in `migrate_all.py` step `[7b]`

**Not migrated or lossy:**

- No line-level product/GST detail (summary lines only).
- Bank receipts, transfers, recon, PDC, POs, stock adjustment — **no real rows in export** (placeholders).
- FA smart settings, taxes, lock dates, users/roles — **snapshot only**, not native settings.
- Full historical GL (only 2 journals in export).

---

## What is remaining

### Priority 1 — Unblock go-live verification ✅ (complete 2026-05-29)

1. ~~Apply Prisma migrations~~ — done via `migrate_deploy.py` / `migrate_status.py`.  
2. ~~Re-run `_reconcile.py`~~ — transactional counts **match** export for tenant `cmpfm1nst0001lhq3rz09938z`.  
3. ~~TB integrity~~ — `_tb_spot_check.py`: debits = credits ✅. AR/AP aging vs FA snapshot **differs** (summary GL) — informational only.  
4. ~~Unified runner~~ — `_go_live_check.py` + `release-check.ps1`.  
5. ~~Migration health~~ — `_migration_health.py`; draft SI/VI documented.  
6. ~~Go-live runbook~~ — `GO-LIVE-RUNBOOK.md`, `DEPLOY-QUICKSTART.md`, `DAY-1-OPERATIONS.md`.

### Priority 2 — Phase 2 Smart Settings (FA §12.2)

- Wire remaining accordions (e-signatures); **product description defaults** on SI + VI create ✅.
- **Draft SR/VP post** — `POST .../post` + **Post to GL** on receipt/payment detail (import drafts) ✅.
- **Template/Draft** on bank, **saleReceipts**, **supplierPayments** ✅ (`post_gl_on_create` + draft status).
- **Import** `supplier_payments` job type (draft VP, post via UI) ✅.
- **Import post to GL** — job `postGl` flag or row `status=posted` for SI/VI/SR/VP ✅.
- **Bulk draft post** — `scripts/fastaccounts_migrate/_bulk_post_drafts.py` (--dry-run) ✅.
- **Round-off sales** on taxed document lines ✅ (`TaxCalculationService` + `roundOffSales`).
- Smart Doc 1–4 on SR/VP ✅; SI/VI/bank already wired.

### Priority 3 — Phase 4 Reports polish

- Full **FA reports hub tree** (expand/collapse, search, 200+ leaves).
- **Drill-down** on more extended report slugs (core grid + statements done).
- Server PDF on remaining extended-only report pages.
- **Budget vs actual** in `reports-catalog.ts` + `/reports/budget-vs-actual` ✅.
- Row-count spot checks vs FA export for top 50 reports.

### Priority 4 — Phase 1 / 2 gaps (behavior)

| Area | Remaining |
|------|-----------|
| Bank | Draft EP/IR/BT post endpoints ✅; recon UX polish; FX wizard |
| Sales/Purchases | Sales All / Purchases All — FA-style filters done; spot-check vs FA export columns |
| Attachments | Confirm all FA doc types including bank×3 + journals |
| Authorisation | ✅ Guards audited via `scripts/_audit_approval_posts.py` |
| COA/Journals | Bulk delete drafts ✅; section move on edit ✅; **journals** Excel import |
| PDC | Dedicated reversal flows beyond bounce |
| Print | ✅ Two-copy SR/VP |

### Priority 5 — Phase 5 add-ons (if licensed in FA)

- Fixed assets, landed cost, letter of credit, consolidation  
- Budget reports (Budget CRUD exists; reporting TBD)

### Priority 6 — Phase 6–8 Integrations & import

- **FBR/PRAL** — SI submit/poll/retry + error queue; readiness cards with `missingEnvKeys`; live when `FBR_PRAL_*` set  
- **PayPro/Kuickpay** — checkout initiate + webhook settlement; readiness on integrations + online-payments pages  
- **Email invoice** — SI detail “Email customer” when enabled in Email settings; Brevo/SMTP required  
- Excel import: SI/SR/VI/VP draft or **postGl** (+ customers, suppliers, products, **opening_stock**, **product_tax_update**, journals, bank EP/IR ✅)  
- SMS automation, Google OAuth, 2FA, developer API keys — deferred (not Nafy-licensed)

### Priority 7 — Phase 8–9 Distribution / pharmacy extras

Only if enabled in FA Smart Settings for tenant:

- Retail margin, trade offer, area qty (width×length)  
- Bundle products, POS mode, Schedule 3 templates  
- Multi-unit price matrix, customer–product lines  

### Priority 8 — Phase 10 Hardening

- `FA-FEATURE-MATRIX.csv` generated and kept current  
- Playwright parity suite in CI (`e2e/parity/*.spec.ts`)  
- Report pagination performance (7k+ invoices)  
- Security review: RBAC, lock date, authorisation  

### Governance / docs

- [x] Generate `Backend/docs/FA-FEATURE-MATRIX.csv` — `python scripts/_generate_feature_matrix.py` (115 rows from plan §3)  
- [ ] Strike completed rows in [PARITY-BACKLOG.md](./PARITY-BACKLOG.md) with PR links  
- [ ] Update §3 status columns in [FA-FULL-PARITY-IMPLEMENTATION-PLAN.md](./FA-FULL-PARITY-IMPLEMENTATION-PLAN.md) as phases close  

---

## Quick reference — key paths

| Topic | Path |
|-------|------|
| Full phased plan | `Backend/docs/FA-FULL-PARITY-IMPLEMENTATION-PLAN.md` |
| Open backlog | `Backend/docs/PARITY-BACKLOG.md` |
| Migration counts | `scripts/fastaccounts_migrate/MIGRATION-AUDIT.md` |
| Go-live runbook | `Backend/docs/GO-LIVE-RUNBOOK.md` |
| Day-1 ops | `Backend/docs/DAY-1-OPERATIONS.md` |
| Deploy quickstart | `Backend/docs/DEPLOY-QUICKSTART.md` |
| Production deploy | `Backend/docs/PRODUCTION-DEPLOYMENT.md`, `Backend/Dockerfile`, `Backend/railway.toml`, `Frontend/vercel.json` |
| Latest sign-off | `Backend/docs/GO-LIVE-SIGNOFF-LATEST.md` (generated) |
| Nafy in-scope sign-off | `Backend/docs/NAFY-IN-SCOPE-SIGNOFF-LATEST.md` (generated) |
| Human UAT checklist | `Backend/docs/NAFY-UAT-CHECKLIST.md` |
| UAT sign-off (generated) | `Backend/docs/NAFY-UAT-SIGNOFF-LATEST.md`, `scripts/record-uat-signoff.ps1` |
| Prod handoff script | `scripts/nafy-prod-handoff.ps1` |
| Deploy orchestrator | `scripts/nafy-deploy.ps1` |
| Parity progress | `Backend/docs/PARITY-PROGRESS-LATEST.md`, `scripts/_parity_progress.py` |
| E2E guide | `Frontend/e2e/README.md` |
| Go-live runner | `scripts/fastaccounts_migrate/_go_live_check.py` |
| Report spot check | `scripts/fastaccounts_migrate/_report_spot_check.py` |
| Migration health | `scripts/fastaccounts_migrate/_migration_health.py` |
| Bulk post drafts | `scripts/fastaccounts_migrate/_bulk_post_drafts.py` (requires `--i-understand-summary-gl-risk`) |
| Reconcile script | `scripts/fastaccounts_migrate/_reconcile.py` |
| TB spot check | `scripts/fastaccounts_migrate/_tb_spot_check.py` |
| AR/AP spot check | `scripts/fastaccounts_migrate/_ar_ap_spot_check.py` |
| Listing catalog | `Backend/src/app/constants/listing_catalog.py` |
| Report definitions | `Backend/src/app/constants/report_definitions.py` |
| Permissions | `Backend/src/app/constants/permission_catalog.py` |
| Report PDF hook | `Frontend/src/lib/hooks/use-report-server-pdf-export.ts` |
| Report drill-down | `Frontend/src/lib/reports/report-drilldown.ts`, `dynamic-report-grid.tsx` |
| Feature matrix CSV | `Backend/docs/FA-FEATURE-MATRIX.csv`, `scripts/_generate_feature_matrix.py` |
| Activity list filters | `Backend/src/app/services/activity_filters.py`, `activity-list-filters.tsx` |

---

## Honest answers to common questions

**“Are all modules transferred?”**  
**No.** All **core transactional data** from the FA export is in the DB (masters, SI/SR/credits, bills/payments, bank payments). Many FA **modules had no export rows** (bank receipts, transfers, PDC, POs, etc.). **Settings** were not fully mapped to native AI-Accounts settings.

**“Is the app at full FA catalog parity?”**  
**No.** Sixteen licensed add-on rows remain (fixed assets, POS, 2FA, SMS automation, etc.). **Nafy in-scope parity is complete (99/99).**

**“Can we go live for pharmacy month-end?”**  
**Yes (GO)** for Nafy-Pharma tenant `cmpfm1nst0001lhq3rz09938z` as of 2026-05-29: `_go_live_check.py` passes (preflight, reconcile, TB, reports). See `GO-LIVE-SIGNOFF-LATEST.md`. ~47 draft SI / 17 draft VI are operational open items, not blockers. Party aging **REVIEW** with summary GL (6 nominals).

---

*Update this file when closing a phase or after each migration/reconcile run.*
