import { expect, test } from "@playwright/test";

/**
 * Batch expiry alerts — requires authenticated storage state (see e2e/README.md).
 */
test.describe("Batch expiry alerts", () => {
  test.skip(
    process.env.PLAYWRIGHT_AUTH_READY !== "1",
    "Set PLAYWRIGHT_AUTH_READY=1 after running e2e/auth.setup.ts",
  );

  test("notifications page loads", async ({ page }) => {
    await page.goto("/notifications");
    await expect(page).not.toHaveURL(/\/login/);
    await expect(page.getByRole("heading", { name: "Notifications" })).toBeVisible();
  });

  test("batches page supports expiry filter query", async ({ page }) => {
    await page.goto("/inventory/batches?filter=expiring");
    await expect(page).not.toHaveURL(/\/login/);
    await expect(page.getByRole("heading", { name: "Batches and expiry" })).toBeVisible();
    await expect(page.getByText(/Showing batches expiring within/i)).toBeVisible();
  });
});
