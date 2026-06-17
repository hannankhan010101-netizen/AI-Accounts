-- Inventory movement report line indexes (Phase 5 follow-up)

CREATE INDEX IF NOT EXISTS "stock_adjustment_lines_product_idx"
  ON "stock_adjustment_lines" ("stock_adjustment_id", "product_code");

CREATE INDEX IF NOT EXISTS "stock_transfer_lines_product_idx"
  ON "stock_transfer_lines" ("stock_transfer_id", "product_code");
