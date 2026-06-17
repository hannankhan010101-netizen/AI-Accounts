import { test as setup, expect } from "@playwright/test";
import fs from "fs";
import path from "path";

const authFile = path.join(__dirname, ".auth", "user.json");

/**
 * Saves browser storage with JWT + company for authenticated E2E.
 *
 * Usage:
 *   PLAYWRIGHT_EMAIL=... PLAYWRIGHT_PASSWORD=... PLAYWRIGHT_COMPANY_ID=cmpfm1nst0001lhq3rz09938z \\
 *   npx playwright test e2e/auth.setup.ts --project=setup
 */
setup("authenticate via API", async ({ page, request }) => {
  const email = process.env.PLAYWRIGHT_EMAIL;
  const password = process.env.PLAYWRIGHT_PASSWORD;
  if (!email || !password) {
    setup.skip(true, "Set PLAYWRIGHT_EMAIL and PLAYWRIGHT_PASSWORD");
  }

  const apiBase = (process.env.PLAYWRIGHT_API_URL ?? "http://127.0.0.1:8000").replace(
    /\/$/,
    "",
  );
  const res = await request.post(`${apiBase}/api/v1/auth/login`, {
    data: { email, password },
  });
  expect(res.ok(), `Login failed: ${res.status()} ${await res.text()}`).toBeTruthy();

  const tokens = (await res.json()) as {
    accessToken: string;
    refreshToken: string;
  };
  const companyId =
    process.env.PLAYWRIGHT_COMPANY_ID ?? "cmpfm1nst0001lhq3rz09938z";

  await page.goto("/login");
  await page.evaluate(
    ({ accessToken, refreshToken, companyId: cid }) => {
      localStorage.setItem("fa.accessToken", accessToken);
      localStorage.setItem("fa.refreshToken", refreshToken);
      localStorage.setItem("fa.currentCompanyId", cid);
    },
    {
      accessToken: tokens.accessToken,
      refreshToken: tokens.refreshToken,
      companyId,
    },
  );

  fs.mkdirSync(path.dirname(authFile), { recursive: true });
  await page.context().storageState({ path: authFile });
});
