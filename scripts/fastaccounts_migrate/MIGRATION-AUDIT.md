# FastAccounts → Nafy-Pharma migration audit

Company: `cmpfl1itj000hqubj7rne8q5f`  
Source: `fastaccounts_export/output/fastaccounts_labeled_data.json` (39,684 records, 28 sections)

## Executive summary

| Area | Status |
|------|--------|
| Master data (customers, suppliers, products, COA, banks) | **Complete** — counts match export |
| Sales invoices / receipts / credits | **Complete** — unique doc numbers match |
| Purchase bills (aggregate + listing) | **Was 18 short** — see gap below |
| Supplier payments | **Complete** — 960/960 |
| Bank payments | **Complete** — 1,500 rows |
| Journals | **2 rows only** in export (placeholder GL) |

Run reconciliation anytime:

```powershell
cd scripts\fastaccounts_migrate
python _reconcile.py
python _check_pp_bills.py   # orphan bills from purchase_payments module
```

---

## Critical gap found (fixed in script)

**18 supplier bills** (~**PKR 1,853,830.60**) appeared only in the `purchase_payments` export section (FA “Purchases → Payments” grid with `Type=Bill`). They were **not** in `purchases_all` or `purchase_bills`, so `migrate_aggregate.py` and the original `migrate_all.py` never imported them.

Bill numbers: `1802, 1826, 1829, 1847, 1861, 1868, 1874, 1877, 1880, 1882, 1886, 1890, 1892, 1897, 1898, 1901, 1903, 1908`

**Fix:** `migrate_all.py` now runs step `[7b] Purchase payments listing (orphan bills)` via `migrate_purchase_payments_listing()`.

**Status:** Backfilled 2026-05-23 — all 18 bills now in DB (706/706 reconcile).

**To backfill on existing DB (idempotent):**

```powershell
cd scripts\fastaccounts_migrate
python migrate_all.py --company-id cmpfl1itj000hqubj7rne8q5f
# (idempotent — skips existing doc numbers; only creates the 18 missing bills)
```

Or run only the new step by temporarily commenting other steps in `run_migration()`.

> **Note:** Re-running full `migrate_all.py` previously duplicated bank payments (no DB dedupe). Fixed in `migrate_bank_payments()` preload + `_dedupe.py` bank payment cleanup. Safe to re-run after this fix.

---

## What migrated successfully

### Scripts used

1. **`migrate_all.py`** — masters, listing modules, bank payments, journals  
2. **`migrate_aggregate.py`** — `sales_all` + `purchases_all` (bulk activity)

### Counts (reconcile 2026-05-23)

| Entity | Export unique | DB | Match |
|--------|---------------|-----|-------|
| Customers | 220 | 220 | ✓ |
| Suppliers | 91 | 91 | ✓ |
| Products | 1,100 | 1,100 | ✓ |
| Bank accounts | 5 | 5 | ✓ |
| Nominals (COA) | 223 | 223 | ✓ |
| Sales invoices | 6,926 | 6,926 | ✓ |
| Sales receipts | 10,260 | 10,260 | ✓ |
| Sales credits | 78 | 78 | ✓ |
| Supplier bills | 688* | 688* | ✓ after 18 backfill → **706** |
| Supplier payments | 960 | 960 | ✓ |
| Bank payments | 1,500 | 1,500 | ✓ |
| Journals | 2 | 2 | ✓ |

\*Before `purchase_payments` fix; full export union = **706** bills.

### `sales_all` doc types (17,203 rows)

- Sale Invoice: 6,864  
- Sale Receipt: 10,260  
- Sale Credit: 41  
- Sale Credit Payment: 38  

### `purchases_all` doc types (1,615 rows)

- Purchase Payment: 960  
- Purchase Invoice: 655  

---

## Intentionally not migrated (no export data)

These modules exported **placeholder rows only** (`Cells` key, 1 record):

- `bank_receipts`, `bank_transfers`, `bank_reconciliation`, `bank_import_statement`
- `pdc_received`, `pdc_issued`
- `purchase_orders`, `stock_adjustment`

`sales_orders` (17,200 rows) is the **same activity grid as `sales_all`** — covered by `migrate_aggregate.py`.

---

## Exported but not migrated (configuration / quality)

| Export section | Records | Notes |
|----------------|---------|--------|
| `settings_smart_settings` | 29 | UI toggles — not mapped to `AppSettings` |
| `settings_taxes` | 20 | Tax/year-end config — not migrated |
| `settings_business_info` | 1 | Business profile — not migrated |
| `settings_lock_date` | 2 | Lock dates — not migrated |
| `settings_users` / `settings_roles` | 1 each | Grid headers only |

---

## Structural limitations (data present, detail lost)

These are **by design** in the current migrators — documents exist but lack full FA fidelity:

1. **Line detail** — Every invoice/bill is a **single summary line** (qty=1, rate=total). No product codes, GST, or multi-line breakdown.  
   - DB check: **0** invoice lines with `productCode`.

2. **GL posting** — ~~Status is `posted` but journals were null after import.~~ **Done** (2026-05-23):  
   `migrate_posting_fast.py` linked **6879/6879 posted SI** + **689/689 posted bills** to GL journals.  
   47 SI remain `draft` (no journal — correct). Smart Settings `defaults` set for AR/Sales/AP/Purchases.

3. **Opening balances** — Customer/supplier `Balance` in export is **not** stored (schema has no opening-balance field on `Customer`/`Supplier`).  
   - 84 customers with non-zero balance (~PKR 11.1M total)  
   - 21 suppliers with non-zero balance  

4. **Stock on hand** — Product `Quantity` / `Low Stock Level` exported but **not** written to inventory (`ProductBatch.quantityOnHand` etc.).  
   - 447 products with qty > 0 in export.

5. **Journals** — Only 2 journals in export; migrated with **hardcoded placeholder nominals** `310101` / `230901`, not real journal lines.

6. **Supplier credits** — None in `purchases_all` for this tenant (0 in export).

---

## Prisma schema vs FA data

- **`budgets` table** — New AI-Accounts module; not in FA export. Apply migration:  
  `python _apply_budget_migration.py` (uses DIRECT_URL; FK references `"Company"` not `companies`)

---

## Recommended follow-up

1. ~~Run `migrate_all.py` again to import the **18 orphan bills**.~~ **Done**
2. ~~Re-run `python _reconcile.py` — bills should show **706/706**.~~ **Done**
3. ~~Backfill **opening AR/AP** and **stock quantities**~~ **Done** via `migrate_supplemental.py`:
   ```powershell
   python migrate_supplemental.py --company-id cmpfl1itj000hqubj7rne8q5f
   ```
   - 447 `OPENING` product batches (stock on hand)
   - Business profile → `Al-Nafay Pharmacy`
   - 84 customer + 21 supplier FA balances → `smart_settings.payload.fastAccountsImport`
   - FA smart settings + taxes snapshots imported
4. ~~Backfill GL journals~~ Use `migrate_posting_fast.py` (batched SQL, ~1 min for full tenant):
   ```powershell
   python migrate_posting_fast.py              # invoices + bills
   python migrate_posting_fast.py --limit 50     # smoke test
   python _cleanup_orphan_journals.py            # after interrupted slow runs
   ```
   Legacy single-doc path: `migrate_posting.py` (slow; use only if debugging).
5. Map FA smart settings rows into native UI toggles (currently stored as import snapshot only).
