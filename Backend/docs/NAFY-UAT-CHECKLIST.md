# Nafy-Pharma — UAT checklist (human sign-off)

**Tenant:** `cmpfm1nst0001lhq3rz09938z`  
**Use after:** production deploy + [`GO-LIVE-SIGNOFF-LATEST.md`](./GO-LIVE-SIGNOFF-LATEST.md) shows **GO**  
**In-scope parity:** [`NAFY-IN-SCOPE-SIGNOFF-LATEST.md`](./NAFY-IN-SCOPE-SIGNOFF-LATEST.md) (auto-generated)

Record pass/fail and initials. One failed **blocker** row keeps release at **NO-GO** until fixed or waived in writing.

---

## A. Login & access

| # | Test | Pass | Initials | Notes |
|---|------|------|----------|-------|
| A1 | Admin login + OTP email received | ☐ | | |
| A2 | Correct company (Nafy-Pharma) selected | ☐ | | |
| A3 | Invite a test user; setup OTP email works | ☐ | | |
| A4 | Module subscriptions / seat count visible | ☐ | | |

---

## B. Daily sales (pharmacy)

| # | Test | Pass | Initials | Notes |
|---|------|------|----------|-------|
| B1 | Open existing posted SI; GL journal link works | ☐ | | |
| B2 | Create draft SI → approve → posts to GL | ☐ | | |
| B3 | Issue goods / COGS on posted SI (if stocked lines) | ☐ | | |
| B4 | Create sales receipt; allocate to open invoice | ☐ | | |
| B5 | Print sales invoice (template renders) | ☐ | | |
| B6 | Email invoice to customer (if Brevo/SMTP live) | ☐ | | Skip if mail not configured |
| B7 | FBR submit on posted SI (if PRAL licensed) | ☐ | | Skip if stub-only |

---

## C. Daily purchases

| # | Test | Pass | Initials | Notes |
|---|------|------|----------|-------|
| C1 | Open posted supplier bill; journal link | ☐ | | |
| C2 | Create draft VI → approve → GL | ☐ | | |
| C3 | Supplier payment + allocation | ☐ | | |
| C4 | GRN flow (if used) | ☐ | | N/A if not used |

---

## D. Bank & month-end

| # | Test | Pass | Initials | Notes |
|---|------|------|----------|-------|
| D1 | Bank payment with multi-line nominals | ☐ | | |
| D2 | Bank receipt | ☐ | | |
| D3 | Reconciliation session: tick / clear / complete | ☐ | | |
| D4 | Trial balance report matches expected totals | ☐ | | |
| D5 | AR aging / customer statement (summary GL = REVIEW OK) | ☐ | | |

---

## E. Settings & controls

| # | Test | Pass | Initials | Notes |
|---|------|------|----------|-------|
| E1 | Smart Settings nominals (230201, 120101, 410101, 510204) | ☐ | | |
| E2 | Lock date blocks back-dated post | ☐ | | |
| E3 | Users / roles: assign role, IP allowlist optional | ☐ | | |
| E4 | Integration readiness page (FBR / PayPro) | ☐ | | |

---

## F. Reports (spot-check)

| # | Test | Pass | Initials | Notes |
|---|------|------|----------|-------|
| F1 | Reports hub → FA modules tree loads | ☐ | | |
| F2 | Sales register / customer performance | ☐ | | |
| F3 | Inventory products list / stock report | ☐ | | |
| F4 | Financial trial balance / GL | ☐ | | |

---

## Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Business owner | | | |
| Finance / accounts | | | |
| Technical lead | | | |

**Overall UAT result:** ☐ **PASS** · ☐ **PASS with waivers** · ☐ **FAIL**

Waivers (if any):

```
```

After completion, store a scanned PDF or signed copy with the project records and record the result:

```powershell
.\scripts\record-uat-signoff.ps1 `
  -BusinessOwner "..." -Finance "..." -TechnicalLead "..." `
  -Result PASS
```

Use `-Result PASS_WITH_WAIVERS -Waivers "..."` when optional rows (B6/B7) are skipped by agreement.

Generated artifact: [`NAFY-UAT-SIGNOFF-LATEST.md`](./NAFY-UAT-SIGNOFF-LATEST.md). Full business release gate: `python scripts/_parity_progress.py --strict-nafy-release` (requires UAT recorded).
