# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: responsive-shell.spec.ts >> responsive shell >> login form inputs meet touch-friendly height
- Location: e2e\responsive-shell.spec.ts:15:7

# Error details

```
Error: expect(received).toBeGreaterThanOrEqual(expected)

Expected: >= 40
Received:    21
```

# Page snapshot

```yaml
- generic [ref=e2]:
  - link "AI-Accounts home" [ref=e4] [cursor=pointer]:
    - /url: /login
    - generic [ref=e5]:
      - img [ref=e7]
      - generic [ref=e8]: AI-AccountsEnterprise-grade AI platform
  - generic [ref=e10]:
    - generic [ref=e11]:
      - heading "Sign in" [level=1] [ref=e12]
      - paragraph [ref=e13]: Welcome back.
    - generic [ref=e14]:
      - generic [ref=e15]:
        - generic [ref=e16]: Email*
        - textbox "Email*" [ref=e17]
      - generic [ref=e18]:
        - generic [ref=e19]: Password*
        - textbox "Password*" [ref=e20]
      - button "Sign in" [ref=e21]
    - generic [ref=e22]:
      - link "Forgot password?" [ref=e23] [cursor=pointer]:
        - /url: /forgot-password
      - link "Create account" [ref=e24] [cursor=pointer]:
        - /url: /signup
```

# Test source

```ts
  1  | import { test, expect } from "@playwright/test";
  2  | 
  3  | /**
  4  |  * Responsive smoke tests — require a running dev server and valid session for (app) routes.
  5  |  * Set PLAYWRIGHT_BASE_URL and optionally storage state with auth for full coverage.
  6  |  */
  7  | test.describe("responsive shell", () => {
  8  |   test("login page fits narrow viewport without horizontal scroll", async ({ page }) => {
  9  |     await page.goto("/login");
  10 |     const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
  11 |     const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
  12 |     expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 2);
  13 |   });
  14 | 
  15 |   test("login form inputs meet touch-friendly height", async ({ page }) => {
  16 |     await page.goto("/login");
  17 |     const email = page.getByLabel(/email/i).first();
  18 |     if (await email.count()) {
  19 |       const box = await email.boundingBox();
> 20 |       expect(box?.height ?? 0).toBeGreaterThanOrEqual(40);
     |                                ^ Error: expect(received).toBeGreaterThanOrEqual(expected)
  21 |     }
  22 |   });
  23 | 
  24 |   test("unauthenticated app routes redirect to login", async ({ page }) => {
  25 |     await page.goto("/dashboard");
  26 |     await page.waitForURL(/\/login/);
  27 |     expect(page.url()).toMatch(/\/login/);
  28 |   });
  29 | });
  30 | 
  31 | test.describe("mobile chrome (authenticated)", () => {
  32 |   test.skip(!process.env.PLAYWRIGHT_AUTH_READY, "Set PLAYWRIGHT_AUTH_READY=1 with valid session");
  33 | 
  34 |   test("bottom navigation visible on dashboard", async ({ page }) => {
  35 |     await page.goto("/dashboard");
  36 |     const nav = page.getByRole("navigation", { name: "Primary navigation" });
  37 |     await expect(nav).toBeVisible();
  38 |     await expect(nav.getByRole("link", { name: "Home" })).toBeVisible();
  39 |   });
  40 | 
  41 |   test("sales invoices list uses card or table region", async ({ page }) => {
  42 |     await page.goto("/sales/invoices");
  43 |     const region = page.getByRole("region", { name: /data (list|table)/i });
  44 |     await expect(region).toBeVisible();
  45 |   });
  46 | 
  47 | });
  48 | 
  49 | test.describe("tablet viewport", () => {
  50 |   test("login page has no bottom navigation chrome", async ({ page }) => {
  51 |     await page.setViewportSize({ width: 1024, height: 768 });
  52 |     await page.goto("/login");
  53 |     await expect(page.getByRole("navigation", { name: "Primary navigation" })).toHaveCount(0);
  54 |   });
  55 | });
  56 | 
```