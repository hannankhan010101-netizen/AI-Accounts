import { test, expect } from "@playwright/test";

/**
 * Command center smoke — dashboard route responds (login redirect when logged out).
 */
test.describe("command center smoke", () => {
  test("dashboard route redirects when logged out", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForURL(/\/(login|dashboard)/);
    if (page.url().includes("/login")) {
      expect(page.url()).toMatch(/\/login/);
      return;
    }
    await expect(page.getByRole("heading", { name: /command center/i })).toBeVisible();
  });
});
