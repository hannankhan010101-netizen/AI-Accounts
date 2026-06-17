# Financial report IDs — capture template

Live **Financial** folder IDs from Fast Accounts are not fully documented in the feature catalog yet. Until a tenant screenshot capture replaces them, the backend uses:

| Strategy | Detail |
|----------|--------|
| **Slug cards** | `TB`, `PNL`, `BS`, `GL`, `FIN_*` resolve to themselves |
| **JSON config** | `Backend/config/financial_report_ids.json` (override via `FINANCIAL_REPORT_IDS_FILE`) |

## When capturing from live UI

1. Open **Reports → Financial** and expand every subgroup.
2. Record each card’s numeric ID and title.
3. Update `Backend/src/app/constants/report_aliases.py` — replace `203`–`210` if live IDs differ.
4. Update `report_financial_registry.FINANCIAL_REPORT_IDS` and `report_definitions.py` `_FINANCIAL_EXTENDED`.
5. Run `pytest src/tests/test_p15_foundation.py src/tests/test_p17_foundation.py`.

## Capture table (fill from tenant)

| Live ID | Report title (UI) | Handler slug |
|---------|-------------------|--------------|
| | Trial Balance | TB |
| | Profit and Loss | PNL |
| | Balance Sheet | BS |
| | General Ledger | GL |
| | | |
