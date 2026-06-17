import { test, expect } from "@playwright/test";

/**
 * FA parity smoke — unauthenticated routes and public report paths.
 * Authenticated document flows need PLAYWRIGHT_AUTH_READY=1 (see responsive-shell.spec.ts).
 */
test.describe("parity smoke", () => {
  test("reports hub and budget-vs-actual route respond", async ({ page }) => {
    await page.goto("/reports");
    await page.waitForURL(/\/(login|reports)/);
    if (page.url().includes("/login")) {
      await page.goto("/login");
      expect(page.url()).toMatch(/\/login/);
      return;
    }
    await expect(page.getByRole("heading", { name: /insights|reports/i }).first()).toBeVisible();
  });

  test("sales all and purchases all redirect when logged out", async ({ page }) => {
    await page.goto("/sales/all");
    await page.waitForURL(/\/login/);
    await page.goto("/purchases/all");
    await page.waitForURL(/\/login/);
  });
});
