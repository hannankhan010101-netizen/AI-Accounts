-- P52: Platform-wide onboarding releases + LLM assistant foundation

CREATE TABLE "platform_onboarding_releases" (
    "id" TEXT NOT NULL,
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

    CONSTRAINT "platform_onboarding_releases_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX "platform_onboarding_releases_release_key_key" ON "platform_onboarding_releases"("release_key");
CREATE INDEX "platform_onboarding_releases_is_active_idx" ON "platform_onboarding_releases"("is_active");
