import { test, expect } from "@playwright/test";

/**
 * Authenticated parity routes — requires saved session from auth.setup.ts.
 *
 *   PLAYWRIGHT_EMAIL=... PLAYWRIGHT_PASSWORD=... npx playwright test e2e/auth.setup.ts --project=setup
 *   PLAYWRIGHT_AUTH_READY=1 npx playwright test e2e/parity/authenticated.spec.ts --project=authenticated
 */
test.describe("authenticated parity", () => {
  test.skip(
    process.env.PLAYWRIGHT_AUTH_READY !== "1",
    "Set PLAYWRIGHT_AUTH_READY=1 after running e2e/auth.setup.ts",
  );

  test("dashboard loads", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).not.toHaveURL(/\/login/);
    await expect(page.getByRole("heading").first()).toBeVisible();
  });

  test("sales invoices list", async ({ page }) => {
    await page.goto("/sales/invoices");
    await expect(page).not.toHaveURL(/\/login/);
    await expect(page.getByRole("region", { name: /data (list|table)/i })).toBeVisible({
      timeout: 15_000,
    });
  });

  test("sales all activity", async ({ page }) => {
    await page.goto("/sales/all");
    await expect(page).not.toHaveURL(/\/login/);
    await expect(page.getByRole("heading", { name: /all sales activity/i })).toBeVisible();
  });

  test("purchases all activity", async ({ page }) => {
    await page.goto("/purchases/all");
    await expect(page).not.toHaveURL(/\/login/);
    await expect(page.getByRole("heading", { name: /all purchase activity/i })).toBeVisible();
  });

  test("reports hub", async ({ page }) => {
    await page.goto("/reports");
    await expect(page).not.toHaveURL(/\/login/);
    await expect(page.getByRole("heading", { name: /insights/i })).toBeVisible();
  });

  test("trial balance report", async ({ page }) => {
    await page.goto("/reports/trial-balance");
    await expect(page).not.toHaveURL(/\/login/);
    await expect(page.getByRole("heading", { name: /trial balance/i })).toBeVisible();
  });

  test("integration status settings", async ({ page }) => {
    await page.goto("/settings/integrations");
    await expect(page).not.toHaveURL(/\/login/);
    await expect(page.getByText(/integration status/i).first()).toBeVisible();
  });
});
