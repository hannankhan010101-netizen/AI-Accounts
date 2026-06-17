# P54 — Workflow document tours

## Shipped (frontend)

| Tour | Start route | Flow |
|------|-------------|------|
| `workflow.sales-invoice` | `/sales/invoices` | New button → navigate → form steps → save |
| `workflow.supplier-bill` | `/purchases/bills` | New button → navigate → form steps → save |

## Engine

- Step action `{ type: "navigate", href }` on **Next** (SPA-safe; tour state persists)
- `DocumentWorkspace` + `GstLineGrid` `data-tour` anchors for workflow steps
- Prerequisites: `onboard.core` + create permission per document type

## Discoverability

- **Tour this page** on list + new routes
- Command palette workflow commands
- Dashboard hint after `onboard.sell` completes
- AI suggestions on `/sales/invoices/new` and `/purchases/bills/new`

## Tests

`Backend/src/tests/test_p54_workflow_tours.py`
