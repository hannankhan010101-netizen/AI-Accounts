import json
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "fastaccounts_export" / "output" / "fastaccounts_labeled_data.json"
d = json.loads(p.read_text(encoding="utf-8"))

for key in ["settings_coa", "settings_journals", "sales_receipts", "bank_payments", "bank_account_balances", "sales_invoices", "purchase_bills"]:
    s = next(x for x in d["sections"] if x["moduleKey"] == key)
    print("\n===", key, "===")
    for i, r in enumerate(s["records"][:3]):
        print(json.dumps(r, ensure_ascii=False)[:500])
