-- P51: Tenant onboarding release CMS

CREATE TABLE "onboarding_release_items" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "release_key" TEXT NOT NULL,
    "version" TEXT NOT NULL DEFAULT '1',
    "title" TEXT NOT NULL,
    "summary" TEXT NOT NULL,
    "published_at" TEXT NOT NULL,
    "tour_id" TEXT,
    "href" TEXT,
    "permissions" JSONB NOT NULL DEFAULT '[]',
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "sort_order" INTEGER NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "onboarding_release_items_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX "onboarding_release_items_company_id_release_key_key" ON "onboarding_release_items"("company_id", "release_key");
CREATE INDEX "onboarding_release_items_company_id_is_active_idx" ON "onboarding_release_items"("company_id", "is_active");

ALTER TABLE "onboarding_release_items" ADD CONSTRAINT "onboarding_release_items_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;
