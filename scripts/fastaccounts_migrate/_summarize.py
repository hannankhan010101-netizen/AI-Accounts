import json
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "fastaccounts_export" / "output" / "fastaccounts_labeled_data.json"
d = json.loads(p.read_text(encoding="utf-8"))
print("sections:", d["totalSections"], "records:", d["totalRecords"])
for s in d["sections"]:
    print(f"  {s['moduleKey']:30} {s['moduleLabel']:25} {s['recordCount']:6}")
    if s["records"]:
        r = s["records"][0]
        print("    sample keys:", list(r.keys())[:12])
