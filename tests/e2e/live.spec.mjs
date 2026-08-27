import { expect, test } from "@playwright/test";

const RAW_ROOT = "https://raw.githubusercontent.com/muzammilafroz/applied-economics-data-learning-lab/v1.0.0";

test("released site, raw data, and Colab target are public", async ({ page, request }) => {
  const data = await request.get(`${RAW_ROOT}/data/teaching/expected_outputs.json`);
  expect(data.ok()).toBeTruthy();
  const expected = await data.json();
  expect(expected.clean_analysis_rows).toBe(1268);

  const notebook = await request.get(`${RAW_ROOT}/notebooks/lessons/01_python_pandas_foundations.ipynb`);
  expect(notebook.ok()).toBeTruthy();
  const source = await notebook.text();
  expect(source).toContain("https://colab.research.google.com/github/muzammilafroz/applied-economics-data-learning-lab/blob/main/notebooks/lessons/01_python_pandas_foundations.ipynb");

  await page.goto("");
  await expect(page).toHaveTitle(/Applied Data Coding Learning Lab/);
  await page.goto("tests/?module=module-01");
  await expect(page.getByRole("heading", { name: "Python and pandas foundations" })).toBeVisible();
});

test("released JupyterLite executes against versioned raw GitHub data", async ({ page }) => {
  await page.goto("lab/lab/index.html?path=_ci/runtime_smoke.ipynb");
  await expect(page.locator(".jp-RenderedHTMLCommon h1", { hasText: "Browser runtime smoke check" }).first()).toBeVisible({ timeout: 120_000 });
  await page.locator(".lm-MenuBar-itemLabel", { hasText: "Run" }).click();
  await page.getByText("Run All Cells", { exact: true }).click();
  const selectKernel = page.getByRole("button", { name: /Select/i });
  if (await selectKernel.isVisible({ timeout: 5_000 }).catch(() => false)) {
    await selectKernel.click();
  }
  await expect(page.getByText(/JUPYTERLITE_SMOKE_OK/)).toBeVisible({ timeout: 240_000 });
});
