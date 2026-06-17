-- P48 user_onboarding_states (FKs use Prisma table names Company / User)

CREATE TABLE IF NOT EXISTS "user_onboarding_states" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "payload" JSONB NOT NULL DEFAULT '{}',
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "user_onboarding_states_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX IF NOT EXISTS "user_onboarding_states_company_id_user_id_key"
    ON "user_onboarding_states"("company_id", "user_id");
CREATE INDEX IF NOT EXISTS "user_onboarding_states_company_id_idx"
    ON "user_onboarding_states"("company_id");

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'user_onboarding_states_company_id_fkey'
    ) THEN
        ALTER TABLE "user_onboarding_states"
            ADD CONSTRAINT "user_onboarding_states_company_id_fkey"
            FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'user_onboarding_states_user_id_fkey'
    ) THEN
        ALTER TABLE "user_onboarding_states"
            ADD CONSTRAINT "user_onboarding_states_user_id_fkey"
            FOREIGN KEY ("user_id") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
    END IF;
END $$;
