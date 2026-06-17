import json
from modules_manifest import ALL_MODULES

d = json.load(open("output/fastaccounts_labeled_data.json", encoding="utf-8"))
print("=== SECTIONS ===")
for s in d["sections"]:
    print(f"  {s['category']:12} | {s['moduleLabel']:30} | {s['recordCount']:5}")

print("\n=== SAMPLES ===")
for key in ["customers", "suppliers", "sales_invoices", "purchase_bills", "sales_receipts", "purchase_payments", "products"]:
    sec = next((s for s in d["sections"] if s["moduleKey"] == key), None)
    if not sec:
        print(f"{key}: MISSING")
        continue
    r = sec["records"][0]
    print(f"\n{sec['moduleLabel']} [{sec['category']}]")
    print(json.dumps(r, indent=2, ensure_ascii=False)[:500])

exported = {s["moduleKey"] for s in d["sections"]}
print("\n=== NOT IN LABELED FILE ===")
for m in ALL_MODULES:
    if m.key not in exported:
        print(f"  {m.label} ({m.category})")
