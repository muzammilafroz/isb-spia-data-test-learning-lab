import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "tests/e2e",
  timeout: 300_000,
  expect: { timeout: 20_000 },
  fullyParallel: false,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["line"], ["html", { open: "never" }]] : "line",
  use: {
    baseURL: process.env.LIVE_SITE ?? "http://127.0.0.1:8000/applied-economics-data-learning-lab/",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
  ],
  webServer: process.env.LIVE_SITE ? undefined : {
    command: "uv run python scripts/serve_site.py --port 8000",
    url: "http://127.0.0.1:8000/applied-economics-data-learning-lab/",
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
