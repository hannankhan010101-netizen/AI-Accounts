import { test, expect } from "@playwright/test";

/**
 * Responsive smoke tests — require a running dev server and valid session for (app) routes.
 * Set PLAYWRIGHT_BASE_URL and optionally storage state with auth for full coverage.
 */
test.describe("responsive shell", () => {
  test("login page fits narrow viewport without horizontal scroll", async ({ page }) => {
    await page.goto("/login");
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 2);
  });

  test("login form inputs meet touch-friendly height", async ({ page }) => {
    await page.goto("/login");
    const email = page.getByLabel(/email/i).first();
    if (await email.count()) {
      const box = await email.boundingBox();
      expect(box?.height ?? 0).toBeGreaterThanOrEqual(40);
    }
  });

  test("unauthenticated app routes redirect to login", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForURL(/\/login/);
    expect(page.url()).toMatch(/\/login/);
  });
});

test.describe("mobile chrome (authenticated)", () => {
  test.skip(!process.env.PLAYWRIGHT_AUTH_READY, "Set PLAYWRIGHT_AUTH_READY=1 with valid session");

  test("bottom navigation visible on dashboard", async ({ page }) => {
    await page.goto("/dashboard");
    const nav = page.getByRole("navigation", { name: "Primary navigation" });
    await expect(nav).toBeVisible();
    await expect(nav.getByRole("link", { name: "Home" })).toBeVisible();
  });

  test("sales invoices list uses card or table region", async ({ page }) => {
    await page.goto("/sales/invoices");
    const region = page.getByRole("region", { name: /data (list|table)/i });
    await expect(region).toBeVisible();
  });

});

test.describe("tablet viewport", () => {
  test("login page has no bottom navigation chrome", async ({ page }) => {
    await page.setViewportSize({ width: 1024, height: 768 });
    await page.goto("/login");
    await expect(page.getByRole("navigation", { name: "Primary navigation" })).toHaveCount(0);
  });
});
