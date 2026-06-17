import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:3000";
const authFile = "e2e/.auth/user.json";
const smokeOnly = process.env.PLAYWRIGHT_SMOKE_ONLY === "1";

const projects: Parameters<typeof defineConfig>[0]["projects"] = [];

if (smokeOnly) {
  projects.push({
    name: "smoke",
    use: { ...devices["Desktop Chrome"] },
    testMatch: /parity\/smoke\.spec\.ts/,
  });
} else {
  projects.push(
    {
      name: "setup",
      testMatch: /auth\.setup\.ts/,
    },
    {
      name: "mobile",
      use: { ...devices["Pixel 5"], browserName: "chromium" },
    },
    {
      name: "tablet",
      use: { ...devices["iPad (gen 7) landscape"], browserName: "chromium" },
    },
  );

  if (process.env.PLAYWRIGHT_AUTH_READY === "1") {
    projects.push({
      name: "authenticated",
      testMatch: /authenticated\.spec\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        storageState: authFile,
      },
      dependencies: ["setup"],
    });
  }
}

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  reporter: "list",
  use: {
    baseURL,
    trace: "on-first-retry",
  },
  projects,
  webServer: process.env.CI
    ? undefined
    : {
        command: "npm run dev",
        url: baseURL,
        reuseExistingServer: true,
        timeout: 120_000,
      },
});
