import { test, expect } from "@playwright/test";

test.describe("Inventory add", () => {
  test("add page loads", async ({ page }) => {
    await page.goto("/inventory/add");
    await expect(page.getByRole("heading", { name: "Add product" })).toBeVisible();
    await expect(page.getByLabel(/Name/i)).toBeVisible();
    await expect(page.getByLabel(/Sale price/i)).toBeVisible();
  });
});
