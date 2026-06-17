-- Assembly finished-product batch/expiry on jobs (FA §11).
ALTER TABLE "assembly_jobs" ADD COLUMN IF NOT EXISTS "batch_number" TEXT;
ALTER TABLE "assembly_jobs" ADD COLUMN IF NOT EXISTS "expiry_date" TIMESTAMP(3);
