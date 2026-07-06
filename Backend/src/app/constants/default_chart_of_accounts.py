"""Default chart of accounts + Smart Settings posting defaults for new companies.

Seeded at company bootstrap so a brand-new company can post sales invoices,
supplier bills, COGS, stock adjustments and FX entries immediately, instead of
hitting "set Smart Settings → Defaults" / "unknown nominal code" errors.

Structure: category (with P&L/BS ``type``) → section → nominal accounts.
Nominal ``code`` values are unique per company and are what the posting engine
and ``DEFAULT_POSTING_DEFAULTS`` reference.
"""

from __future__ import annotations

# type: Income / Expense / Asset / Liability / Equity / Other
DEFAULT_CHART: list[dict] = [
    {
        "code": "1",
        "name": "Assets",
        "type": "Asset",
        "sections": [
            {
                "code": "10",
                "name": "Current Assets",
                "nominals": [
                    {"code": "1100", "name": "Accounts Receivable"},
                    {"code": "1200", "name": "Inventory"},
                    {"code": "1300", "name": "GST Input (Sales Tax Receivable)"},
                    {"code": "1400", "name": "Bank"},
                    {"code": "1450", "name": "Cash in Hand"},
                ],
            },
            {
                "code": "15",
                "name": "Non-Current Assets",
                "nominals": [
                    {"code": "1600", "name": "Property, Plant & Equipment"},
                ],
            },
        ],
    },
    {
        "code": "2",
        "name": "Liabilities",
        "type": "Liability",
        "sections": [
            {
                "code": "20",
                "name": "Current Liabilities",
                "nominals": [
                    {"code": "2100", "name": "Accounts Payable"},
                    {"code": "2200", "name": "GST Output (Sales Tax Payable)"},
                ],
            },
        ],
    },
    {
        "code": "3",
        "name": "Equity",
        "type": "Equity",
        "sections": [
            {
                "code": "30",
                "name": "Equity",
                "nominals": [
                    {"code": "3100", "name": "Owner's Capital"},
                    {"code": "3200", "name": "Retained Earnings"},
                ],
            },
        ],
    },
    {
        "code": "4",
        "name": "Income",
        "type": "Income",
        "sections": [
            {
                "code": "40",
                "name": "Revenue",
                "nominals": [
                    {"code": "4000", "name": "Sales"},
                    {"code": "4900", "name": "Foreign Exchange Gain"},
                ],
            },
        ],
    },
    {
        "code": "5",
        "name": "Expenses",
        "type": "Expense",
        "sections": [
            {
                "code": "50",
                "name": "Cost of Sales",
                "nominals": [
                    {"code": "5000", "name": "Cost of Goods Sold"},
                    {"code": "5100", "name": "Purchases"},
                    {"code": "5200", "name": "Stock Adjustments"},
                ],
            },
            {
                "code": "60",
                "name": "Operating Expenses",
                "nominals": [
                    {"code": "6900", "name": "Foreign Exchange Loss"},
                ],
            },
        ],
    },
]

# Smart Settings ``payload["defaults"]`` → nominal codes above. Keys match those
# required by PostingPrerequisitesService.
DEFAULT_POSTING_DEFAULTS: dict[str, str] = {
    "receivablesNominalCode": "1100",
    "inventoryNominalCode": "1200",
    "gstInputNominalCode": "1300",
    "payablesNominalCode": "2100",
    "gstOutputNominalCode": "2200",
    "salesNominalCode": "4000",
    "fxGainNominalCode": "4900",
    "cogsNominalCode": "5000",
    "purchasesNominalCode": "5100",
    "stockAdjustmentNominalCode": "5200",
    "fxLossNominalCode": "6900",
}
