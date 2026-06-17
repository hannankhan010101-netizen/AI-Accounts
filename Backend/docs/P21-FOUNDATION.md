# P21 — Delivery stock, manual GRN on bill void, admin mutator gates (implemented)

Builds on [P20-FOUNDATION.md](./P20-FOUNDATION.md).

## Shipped

| ID | Capability | API / code |
|----|------------|------------|
| P21.1 | **Delivery stock on create** | `POST /delivery-notes` applies `apply_delivery_note_lines` (batch qty reduced); response `stockIssued` |
| P21.2 | **Delivery stock on void** | Void paths restore stock (`stockRestored` / `deliveryStockRestored`) |
| P21.3 | **Manual GRN on bill void** | `void_supplier_bill` also voids `manual` GRNs with `sourceId = bill_id` |
| P21.4 | **Broader module gates** | bank accounts, attachments, import jobs, document numbers, report runs, custom fields, product UOMs |

## Delivery note stock

On create, each line with `productCode` and positive `quantity` reduces `ProductBatch` quantity (outbound delivery).

On void (standalone, invoice void, or SO cancel), quantities are restored before status is set to `voided`.

## Supplier bill void + manual GRN

In addition to `GRNVI` notes (P18), bills may have **`manual`** goods receipt notes linked via `sourceId`. These are voided and stock-rolled back the same way.

## Module gates (P21)

| Route | Module |
|-------|--------|
| `POST /bank-accounts` | bank |
| `POST /attachments` | financial |
| `POST /import-jobs` | financial |
| `POST /import-jobs/upload` | financial |
| `POST /document-numbers/next` | financial |
| `POST /reports/runs` | financial |
| `PATCH /customers/{id}/custom-fields` | sales |
| `PATCH /products/{id}/custom-fields` | inventory |
| `POST /products/{id}/uoms` | inventory |

## Next (P22)

See [P22-FOUNDATION.md](./P22-FOUNDATION.md).
