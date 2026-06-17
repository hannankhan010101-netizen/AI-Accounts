# Final parity plan — AI-Accounts vs FastAccounts

**Audit date:** 2026-05-23  
**Scope:** Nafy-Pharma tenant + full product parity with `FAST-ACCOUNTS-FEATURE-CATALOG.md`  
**Automated checks run:** `_route_audit.py`, `_wave1_connectivity.py`, `_settings_connectivity.py`, `_deep_audit_reports.py`, `tsc --noEmit`

---

## Executive summary

| Layer | Status | Notes |
|-------|--------|-------|
| **Navigation (116 hrefs)** | ✅ 0 stubs | 35 sidebar + 52 settings + 29 report shortcuts |
| **FA §2.1 sidebar (24 items)** | ✅ 24/24 | Plus 11 extra operational tabs in AI |
| **§10.11 catalog SQL handlers** | ✅ 59/59 via aliases | 1 alias bug: report `149` → dead handler `081` |
| **Report definitions (84 rows)** | ⚠️ 83/84 | `149` Product Activity Summary broken |
| **Backend APIs without UI** | ⚠️ Large | Assembly, FX reval, Projects/Locations (schema only), attachments |
| **FA add-on modules** | ❌ Missing | Landed cost, LC, fixed assets, budget, authorisation UI |
| **Integrations** | ⚠️ Stub mode | FBR, PayPro/Kuickpay, sent emails, Stripe billing |
| **TypeScript build** | ❌ 4 errors | `settings/migrations/page.tsx` only |

**Recommended delivery:** 8 phases over ~12–16 weeks (parallelizable). Phase 0–2 unblock pharmacy daily ops; Phase 3–5 add-ons; Phase 6–8 hardening.

---

## Phase 0 — Confirmed bugs (fix first, ~2–3 days)

| ID | Bug | Status |
|----|-----|--------|
| B0.1 | **Report alias chain broken** (`149`→`081`→`080`) | ✅ Fixed — chained `resolve_report_handler_id` + test |
| B0.2 | **TypeScript: migrations page** | ✅ Fixed |
| B0.3 | **`_parity_audit.py` crashes** | ✅ Fixed |
| B0.4 | **Dashboard layout / widget gating** | ✅ Fixed — layout API uses dashboard settings; home respects widgets |
| B0.5 | **Sent emails log** | ✅ Partial — logs on successful resend-invite; full SMTP catalog triggers Phase 5 |
| — | **`/reports/execute` SyntaxError** (param order) | ✅ Fixed |

---

## Phase 1 — API–UI wiring (backend exists, ~2 weeks)

| Feature | Status |
|---------|--------|
| **Assembly templates & jobs** | ✅ `/inventory/assembly/templates`, `/jobs`, `assemblyApi` |
| **FX revaluation** | ✅ `/bank/fx-revaluation`, `fxRevaluationApi` |
| **Projects** | ✅ `GET/POST/PATCH /projects`, `/settings/projects` |
| **Locations** | ✅ `GET/POST/PATCH /locations`, `/settings/locations` |
| **Attachments** | ✅ Upload/list/download + panel on SI, quotations, orders, credits |
| **Assembly reports** | Open — extend catalog links |

**CI:** `python scripts/_phase1_connectivity.py` — PASS. Route audit: **38** nav + **54** settings links, 0 stubs.

---

## Phase 2 — Operational depth & FA document parity (~3 weeks)

From `PARITY-BACKLOG.md` — same tabs, incomplete behavior:

### 2.1 Bank
- [ ] Reconciliation **session** UX (match rules, complete session) beyond import statement
- [x] Bank payment **multi-line nominal split** — UI + `nominalLines` API + split GL posting
- [ ] Excel **voucher** import (distinct from statement feed §2.1)
- [ ] FX revaluation UI (Phase 1) + multi-currency setup wizard (§4.6–4.7)

### 2.2 Sales / Purchases
- [ ] **Sales All / Purchases All** — confirm FA aggregate semantics (unified filters vs activity feed)
- [ ] **ADT / FED / WHT** on invoice/bill lines + GL legs
- [ ] **Retail margin** / discount rules (Smart Settings dependencies)
- [ ] **Batch sales invoice** (§3.9 cross-cutting)
- [ ] **Transaction templates** + full **recurring** scheduler (not only missed recurrence)
- [ ] Delivery note vs goods-issue **stock guards** (P20–P22 backlog items)

### 2.3 Post-dated cheques
- [x] Register, present, clear
- [x] **Mark bounced** on PDC detail
- [ ] Dedicated **reversal** flows (beyond status dropdown)

### 2.4 GL / COA
- [ ] Journal **edit / copy / bulk-delete** with constraints
- [ ] COA section **bulk-delete**, **inter-category move**
- [ ] Nominal **edit**, move-between-sections, auto-code preview
- [ ] **Per-user lock date** extension (global lock exists)
- [ ] Re-post when draft gets defaults after create

### 2.5 Approvals
- [ ] **Authorisation** add-on: draft → approve matrix per doc type (§12.6)
- [ ] **Advance users** data visibility (§12.5)
- [ ] Settings screens + runtime gates

**Acceptance:** Pharmacy UAT script covering SI→SR allocation, VI→VP, PDC clear, GRN→bill, month-end TB/PL/BS.

---

## Phase 3 — Missing FA modules (schema + UI, ~4–6 weeks)

No Prisma models today — greenfield:

| Module | FA reference | Work |
|--------|--------------|------|
| **Budget** | §9.3, Settings Budget | `Budget`, `BudgetLine` models; replace `list_budgets_stub`; reports category |
| **Fixed assets** | §8, §15 | Register, depreciation run, disposal, GL linkage, reports |
| **Landed cost** | §2.6 Inventory | LC allocation to receipts/bills |
| **Letter of credit** | §2.6, Inventory reports | LC register, drawdown, GRN link |
| **Consolidation reports** | §10 | Multi-company (if in scope) |

**Acceptance:** Module flags in `module-subscriptions`; gated APIs; minimal report per module.

---

## Phase 4 — Settings & admin completion (~2 weeks)

| Item | Current | Target |
|------|---------|--------|
| OP Methods | Page exists, purpose unclear | Document + implement FA options |
| Filters vs Columns vs Content | Three pages | Single source of truth; prevent drift |
| Dashboard Management | Saves widget IDs | Live `/dashboard` reads same config |
| User log | Works | Full **Type** enum, **View** deep links, retention policy |
| Roles | CRUD mostly done | Fully expanded permission trees per submodule |
| Add user | Works | Confirm role on add vs edit (FA §12.3) |
| **Budget / Authorisation / Location / Advance users** | Missing from menu | Add to `settings-menu.ts` + pages |

---

## Phase 5 — Integrations & email (~2–3 weeks)

| Integration | Current | Production target |
|-------------|---------|-------------------|
| **FBR/PRAL** | Stub mode in `fbr_service.py` | Live API, vault for credentials, error dashboard wired |
| **PayPro / Kuickpay** | Stub checkout | Webhooks, auto receipt + allocation UI |
| **Email add-on** | Settings UI; no dispatch | SMTP/SES, triggers, throttling, populate `sent-emails` |
| **Stripe billing** | Dev stub sessions | Real checkout + portal for SaaS (if product scope) |
| **Forgot password** | OTP TBD in `auth.py` | Email OTP flow |

---

## Phase 6 — Reports & analytics (~2 weeks)

- [x] §10.11 numeric IDs — SQL handlers (fix B0.1)
- [ ] Enumerate **remaining FA report tree** (Bank/Financial/Assembly/Projects/Budget/FA/Consolidation) into `report_definitions.py`
- [ ] Wire `POST /reports/runs/{id}/export` in UI (noted in PRINT-EXPORT-MATRIX)
- [ ] Analytical hub: dedicated pages for high-traffic IDs vs generic runner only
- [ ] Server-side PDF (optional; currently browser print only)

---

## Phase 7 — Auth, API users, commercial (~1–2 weeks)

| Feature | Status |
|---------|--------|
| Google Sign-In | Not implemented |
| 2FA | Not implemented |
| API users + OTP + IP restrict | §1.4 — partial via users module |
| Subscription gates on **all** mutators | Partial (`require_module_access`) |
| Notifications bell | Unverified |

---

## Phase 8 — QA, migration, CI (~ongoing)

### Automated gates (add to CI)
```bash
python scripts/_route_audit.py
python scripts/_wave1_connectivity.py
python scripts/_settings_connectivity.py
python scripts/_deep_audit_reports.py
cd Frontend && npx tsc --noEmit
cd Backend && pytest src/tests/test_p0_foundation.py -q  # expand over time
```

### Data migration (Nafy-Pharma)
- [ ] Re-run `_reconcile.py` after each major schema change
- [ ] Spot-check: open balances = FA trial balance for lock date
- [ ] Document numbers: 0 missing (already achieved)

### E2E smoke (Playwright)
- Login → create SI → receipt allocate → TB
- VI → payment → AP aging
- Bank import statement → reconcile one line
- Print SI / VI PDF

---

## FastAccounts tab checklist (master)

### Sidebar — all ✅ with pages

| FA | AI route |
|----|----------|
| Dashboard | `/dashboard` |
| Bank (6) | `/bank/*` |
| Sales core (6) | `/sales/*` |
| Purchases core (6) | `/purchases/*` |
| Inventory core (2+) | `/inventory/*` (+ transfer, batches) |
| Reports / Analytical | `/reports`, `/reports/analytical` |

### Extra in AI (not in FA §2.1 screenshot)

Quotations, credits, delivery notes, GRN, accounting nav group, admin — **keep**.

### Missing entirely (plan Phases 1–3)

Assembly ops UI, FX reval UI, Landed cost, LC, Fixed assets, Budget, Authorisation, Advance users, Location settings UI, Batch SI, Transaction templates, full recurrence, 2FA, Google login, SMS.

---

## Priority matrix (what to do first)

```
Impact ↑
  │  P0 bugs (B0.1–B0.5)
  │  P1 Assembly + FX + Projects/Locations API/UI
  │  P2 Pharmacy ops depth (allocations, GRN, PDC, tax lines)
  │  P4 Dashboard wire + sent email
  │  P5 FBR/PayPro production
  │  P3 Add-on modules (only if licensed)
  └────────────────────────────→ Effort
```

---

## Ticket template (for tracking)

```markdown
### [P1-ASM-01] Assembly jobs list page
- **FA ref:** §11, §2.6 Assembly Jobs
- **API:** GET/POST /assembly/jobs
- **UI:** /inventory/assembly/jobs (or /manufacturing/jobs)
- **RBAC:** assembly.jobs.create, assembly.*
- **Tests:** connectivity script + test_p4_foundation
- **Done when:** Create job from template, finish, GL + stock movement visible
```

---

## References

- **`Backend/docs/FA-FULL-PARITY-IMPLEMENTATION-PLAN.md`** — master checklist + Phases 0–10 (every FA feature)
- `FAST-ACCOUNTS-FEATURE-CATALOG.md` §2.1, §2.6, §12.1, §15
- `Backend/docs/PARITY-BACKLOG.md`
- `Backend/docs/PRINT-EXPORT-MATRIX.md`
- Scripts: `scripts/_route_audit.py`, `_deep_audit_reports.py`, `_parity_audit.py`
- Migration: `scripts/fastaccounts_migrate/migrate_all.py`

---

*Update this file when closing phases; strike rows in PARITY-BACKLOG.md with PR links.*
