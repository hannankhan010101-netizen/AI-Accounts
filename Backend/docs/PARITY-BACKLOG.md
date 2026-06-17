# Parity backlog — blocking items for full Fast Accounts API coverage

This file tracks **gaps and TBD endpoints** called out in [FAST-ACCOUNTS-FEATURE-CATALOG.md](../FAST-ACCOUNTS-FEATURE-CATALOG.md) (primarily **section 15** and the **section 16.1** mega-menu footnote). Use it as a ticket index until live UI parity is captured.

## Go-live gates (Nafy-Pharma 2026-05-29)

- ~~`_go_live_check.py` (reconcile + TB + health + reports + integrations)~~ → `GO-LIVE-SIGNOFF-LATEST.md`
- ~~`GO-LIVE-RUNBOOK.md`, migration health, bulk-post safeguards~~
- ~~Import postGl for SI/VI/SR/VP; SR/VP template draft; integration readiness UI~~
- ~~`PRODUCTION-DEPLOYMENT.md`, GitHub Actions CI + manual go-live workflow~~

## Recently completed (UX + API slice)

- ~~KISS UX redesign: EnterpriseGrid, DocumentWorkspace, FADS tokens, command palette, settlement/bank voucher detail~~
- ~~GST on planning docs + credits (migrations `20260522130000`, `20260522140000`)~~
- ~~Journal detail `GET /journals/{id}`; supplier payment detail + allocate~~
- ~~Print: invoice, bill, quotation, SO, PO, sales/supplier credits~~
- ~~Print/export parity: settlements, bank, journal, PDC, logistics, stock; report Print+CSV; list CSV export — [PRINT-EXPORT-MATRIX.md](./PRINT-EXPORT-MATRIX.md)~~
- ~~PDC detail `GET /pdc-received|issued/{id}` + lifecycle UI (present / clear)~~
- ~~P&L + Balance Sheet frontend wired to `GET /reports/profit-and-loss` and `GET /reports/balance-sheet`~~
- ~~Trial Balance + General Ledger report pages~~
- ~~Migrations: use `python -m prisma migrate deploy` — see [MIGRATIONS.md](./MIGRATIONS.md)~~

## Reports

- Enumerate **all** standard report IDs under Bank, Financial, Assembly, Projects, Budget, Fixed Assets, Consolidation, and remaining Sales/Purchases leaves (partial lists exist only for Favorites, Sales → Sales and Customer, Inventory → Products).
- Expand **Analytical Reports** categories beyond sample IDs (272, 300, 475, 477).
- ~~Report **pagination** (`page`, `pageSize`) on query runner — P6.~~ Full §10.11 registry SQL handlers — [P10-FOUNDATION.md](./P10-FOUNDATION.md). Bank numeric IDs `072`–`077` + analytical `300`/`475`/`477` — [P13-FOUNDATION.md](./P13-FOUNDATION.md). Assembly `201`/`202`, Stripe Checkout, category comparative P&L — [P14-FOUNDATION.md](./P14-FOUNDATION.md). Financial `203`–`210`, Stripe portal, category pivot — [P15-FOUNDATION.md](./P15-FOUNDATION.md). Checkout customer sync, credit/SA void, pivot CSV — [P16-FOUNDATION.md](./P16-FOUNDATION.md). Invoice void, stock rollback, Stripe period on checkout — [P17-FOUNDATION.md](./P17-FOUNDATION.md). GRN void on bill, GI-only void, Stripe past_due, financial JSON IDs — [P18-FOUNDATION.md](./P18-FOUNDATION.md). GRNPO cancel void, partial GI line void, Stripe cancelled hard lock, GRN stock on create — [P19-FOUNDATION.md](./P19-FOUNDATION.md). GDNSI/GDNSO void hooks, COGS repost, sales/purchase master gates — [P20-FOUNDATION.md](./P20-FOUNDATION.md). Delivery stock, manual GRN on bill void, bank/import/report gates — [P21-FOUNDATION.md](./P21-FOUNDATION.md). COA/settings/FBR gates, delivery vs GI stock guard — [P22-FOUNDATION.md](./P22-FOUNDATION.md). GRNPO/GRNVI guard, operator entitlements, platform webhook policy — [P23-FOUNDATION.md](./P23-FOUNDATION.md). GRN void route, permission seed doc, manual GRN guard — [P24-FOUNDATION.md](./P24-FOUNDATION.md). Role CRUD, list read permissions, GRN void audit — [P25-FOUNDATION.md](./P25-FOUNDATION.md). Assign role, expanded list gates, permission warnings — [P26-FOUNDATION.md](./P26-FOUNDATION.md). Known codes, user invite, strict role validation — [P27-FOUNDATION.md](./P27-FOUNDATION.md). Invite email, `settings.users.invite`, role clone — [P28-FOUNDATION.md](./P28-FOUNDATION.md). Resend invite, welcome email, role export/batch clone — [P29-FOUNDATION.md](./P29-FOUNDATION.md). Role import, invite templates, RBAC audit — [P30-FOUNDATION.md](./P30-FOUNDATION.md). Welcome template PUT, import preview, audit RBAC filter — [P31-FOUNDATION.md](./P31-FOUNDATION.md). Role file import, audit CSV export, revoke/deactivate user — [P32-FOUNDATION.md](./P32-FOUNDATION.md). Reactivate user, async role import job, paginated users — [P33-FOUNDATION.md](./P33-FOUNDATION.md). Auto async import threshold, reinvite, user search — [P34-FOUNDATION.md](./P34-FOUNDATION.md). Bulk user ops, import job audit, Users UI actions — [P35-FOUNDATION.md](./P35-FOUNDATION.md). Role picker, import job widget, permission-gated UI — [P36-FOUNDATION.md](./P36-FOUNDATION.md). Role editor, resend invite, import audit links — [P37-FOUNDATION.md](./P37-FOUNDATION.md). Clone role, invite templates UI, audit navigation — [P38-FOUNDATION.md](./P38-FOUNDATION.md). User deep link, role export/preview, email preview — [P39-FOUNDATION.md](./P39-FOUNDATION.md). Batch role clone, reinvite UI, audit doc links — [P40-FOUNDATION.md](./P40-FOUNDATION.md). Import toolbar, email lookup, bank receipt detail — [P41-FOUNDATION.md](./P41-FOUNDATION.md). Bank payment detail, export-json role clone, reinvite by email — [P42-FOUNDATION.md](./P42-FOUNDATION.md). Bank transfer detail, clone-by-name, user log presets — [P43-FOUNDATION.md](./P43-FOUNDATION.md). Transfer audit, log bookmarks, names-only export — [P44-FOUNDATION.md](./P44-FOUNDATION.md). Payment/receipt audit, saved log presets, names-only import — [P45-FOUNDATION.md](./P45-FOUNDATION.md). Reconciliation audit, preset export, import hint — [P46-FOUNDATION.md](./P46-FOUNDATION.md). Preset import, recon complete, bank recon filter — [P47-FOUNDATION.md](./P47-FOUNDATION.md).

## Operational documents

- ~~**Post-dated cheques (PDCR / PDCI):** register → present → clear with receipt/payment link on clear~~. Bounce/reversal dedicated flows still open.
- **Bank:** ~~POST bank payments + receipts + transfers (header) with GL posting~~. Reconciliation session APIs; statement import; FX revaluation wizard still open. Multi-line bank-payment nominal split still open.
- **Sales / Purchases:** ~~POST sales invoice + receipt + credit with GL posting~~, ~~POST supplier bill + payment + credit with GL posting~~, ~~quotations + sales orders + purchase orders with status lifecycle~~, ~~quotation → SO and SO → invoice and PO → bill conversions~~, ~~master creates~~, ~~FIFO + explicit allocation of receipts/payments against open invoices/bills, plus per-invoice remaining in AR/AP aging~~, ~~GST on SI/VI lines with GL tax legs (Sprint 10)~~, ~~GST on planning docs + credits (lines + UI)~~, ~~explicit-allocation UI on receipt/payment forms (Sprint 13)~~. Delivery notes (GDNSI / GDNSO), Goods Receipt Notes (GRNPO / GRNVI), **Sales All / Purchases All** aggregate semantics still open. ADT/FED/WHT on lines, discounts, retail margin still open.

## GL spine

- ~~Lock Date server-side enforcement on every doc-creating route (sales invoice, supplier bill, bank payment, journal).~~ Per-user lock-date extension still open.
- ~~Posting service writing balanced journals on document create when default nominals are configured.~~ Re-post-on-update when a previously unposted doc gets defaults still open.
- ~~CoaCategory.categoryType (Income/Expense/Asset/Liability/Equity/Other) editable inline; drives P&L + Balance Sheet classification.~~

## GL / COA

- **Nominals** vs **Chart of Account** route parity (section 9.1.3).
- ~~Journal **add** line grid (debit/credit, balance enforcement) — frontend `/settings/journals/new` posts to `/journals`.~~ Edit/copy/bulk-delete constraints still open.
- ~~Section **reorder** persistence — `PUT /coa/sections/{id}/reorder` swaps neighbours within a category.~~ Bulk-delete and inter-category move still open.
- ~~Nominal account **create** modal — `POST /coa/nominals`.~~ Edit / move-between-sections / auto-code preview still open.

## Settings / admin

- **OP Methods** screen purpose and options.
- **Dashboard Management** — widget catalog, ordering, role visibility.
- **Filters Management** vs **Column Management** vs **Content Settings** overlap.
- **Add user** flow: confirm where **role** is assigned (add vs edit).
- ~~Users / roles list from CompanyMembership~~. Role edit/delete and fully expanded permission trees with exact verbs still open.
- **User log:** full `Type` enum, `View` navigation target, export, retention, PII policy.
- **Authorisation** and **Advance users** runtime APIs when add-ons are modeled.

## Integrations and add-ons

- ~~**Digital invoicing (FBR/PRAL)** submit, poll, retry queue, error dashboard — [P8-FOUNDATION.md](./P8-FOUNDATION.md).~~ Exponential backoff + `abandoned` cap — [P9-FOUNDATION.md](./P9-FOUNDATION.md); external vault (AWS/Vault) still open.
- ~~**Online payments (PayPro/Kuickpay)** initiate, webhook, auto receipt + FIFO allocation — [P7-FOUNDATION.md](./P7-FOUNDATION.md).~~ Webhook explicit allocations + receipt allocate UI — P9; rotation runbook — [PAYPRO-CREDENTIAL-ROTATION.md](./PAYPRO-CREDENTIAL-ROTATION.md).
- **Emails** add-on triggers, templates, throttling.
- **Fixed assets:** depreciation, disposal, GL linkage (register screens per section 15).

## Assembly

- ~~Operational **templates** and **jobs** APIs~~ ([P4](./P4-FOUNDATION.md), multi-line GL [P5](./P5-FOUNDATION.md)).

## Multi-tenant / product

- **Operator / administrator** areas not in the public catalog.
- ~~Subscription **gates** per module~~ — `require_module_access` on core document creates + integrations — [P12-FOUNDATION.md](./P12-FOUNDATION.md); extend to all mutators still open.

---

**Process:** Close each row with a link to the OpenAPI operationId and Prisma migration when implemented, then remove or strike the row here.
