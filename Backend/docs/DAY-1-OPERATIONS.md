# Day-1 operations — Nafy-Pharma

After production deploy ([DEPLOY-QUICKSTART.md](./DEPLOY-QUICKSTART.md)). Tenant: `cmpfm1nst0001lhq3rz09938z`.

---

## 1. Smoke the deployment

```powershell
python scripts/_post_deploy_smoke.py --api-url https://your-api-host
.\scripts\go-live.ps1
```

`go-live.ps1` runs in-scope parity (`--strict-nafy`) then migration/TB/report checks.

Confirm [`GO-LIVE-SIGNOFF-LATEST.md`](./GO-LIVE-SIGNOFF-LATEST.md) shows **GO** (AR/AP **REVIEW** is OK on summary GL).

Complete human UAT using [`NAFY-UAT-CHECKLIST.md`](./NAFY-UAT-CHECKLIST.md) before handing to business users.

---

## 2. First login

1. Open production frontend `/login`.
2. Sign in with an account that has access to **Nafy-Pharma** (e.g. migrated admin).
3. Brevo must send OTP — if mail fails, check Railway `BREVO_*` and spam folder.
4. Confirm company selector shows the pharmacy tenant.

**New users:** Settings → Users → invite (requires `settings.users.invite` permission).

---

## 3. Smart Settings sanity check

Settings → **Smart settings** — posting defaults (already verified by preflight):

| Default | Expected code |
|---------|----------------|
| Receivables | `230201` |
| Payables | `120101` |
| Sales | `410101` |
| Purchases | `510204` |

Bank accounts: **5** configured with nominal codes.

Template/draft behaviour: bank, sales receipts, supplier payments use **post on create** when defaults are set.

---

## 4. Daily pharmacy workflows (in scope)

| Task | Where |
|------|--------|
| Sales invoices / receipts | Sales |
| Supplier bills / payments | Purchases |
| Bank payments & receipts | Bank |
| Trial balance | Reports → Trial balance |
| P&L / Balance sheet | Reports |
| Customer / supplier statements | Reports |
| Sales / Purchases **All** (filtered activity) | Sales / Purchases → All |
| Import historical rows | Settings → Import jobs |

**Draft documents (~47 SI, ~17 VI):** open items from FA migration. Approve in the UI when they should post to GL. Do **not** run bulk-post on summary GL without ops approval.

---

## 5. Month-end checklist

- [ ] Trial balance balances (TB spot check or report)
- [ ] P&L and balance sheet for the period
- [ ] Key party statements spot-checked (aging may differ from FA snapshot — **REVIEW**)
- [ ] Bank reconciliations for active accounts
- [ ] New documents posted via approve/import, not bulk script

---

## 6. Integrations (enable when ready)

| Integration | When | Settings |
|-------------|------|----------|
| FBR/PRAL | Sandbox or prod credentials | Leave disabled until keys; stub mode for UAT |
| PayPro / Kuickpay | Merchant + webhook URL | Integration status + Online payments |
| Email add-on | Future parity | Not required for OTP (Brevo handles auth) |

Check: Settings → **Integration status** or `GET .../integrations/readiness`.

---

## 7. Support and escalation

| Issue | Action |
|-------|--------|
| API down | Railway logs; `GET /health` |
| OTP not received | Brevo sender verification, `BREVO_*` env |
| Report empty | Date range, permissions, module enabled |
| AR/AP vs FA mismatch | Expected on summary GL; use TB + doc counts for sign-off |
| Schema drift | [MIGRATIONS.md](./MIGRATIONS.md), `migrate_deploy.py` |

Parity tracker: [AI-ACCOUNTS-PARITY-STATUS.md](./AI-ACCOUNTS-PARITY-STATUS.md)

---

## Related

- [GO-LIVE-RUNBOOK.md](./GO-LIVE-RUNBOOK.md) — verification scripts
- [PRODUCTION-DEPLOYMENT.md](./PRODUCTION-DEPLOYMENT.md) — hosting detail
- [Frontend/e2e/README.md](../../Frontend/e2e/README.md) — optional UI smoke (`PLAYWRIGHT_AUTH_READY=1`)
