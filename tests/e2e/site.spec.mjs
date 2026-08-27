import fs from "node:fs";
import path from "node:path";

import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const quiz = JSON.parse(fs.readFileSync(path.join("web", "assets", "quiz-spec.v1.json"), "utf8"));

function wrongValue(question) {
  if (question.type === "integer" || question.type === "float") return "999999";
  if (question.type === "multi-select") return [question.choices.at(-1).value];
  if (question.type === "multiple-choice") {
    return question.choices.find((choice) => choice.value !== question.answer).value;
  }
  return "deliberately wrong";
}

async function fillQuestion(page, question, value) {
  if (question.type === "multi-select") {
    for (const selected of value) {
      await page.locator(`input[name="${question.question_id}"][value="${selected}"]`).check();
    }
  } else if (question.type === "multiple-choice") {
    await page.locator(`input[name="${question.question_id}"][value="${value}"]`).check();
  } else {
    await page.locator(`[name="${question.question_id}"]`).fill(String(value));
  }
}

test("test center is accessible and fits a phone viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("");
  await expect(page).toHaveTitle(/Applied Data Coding Learning Lab/);
  const bookOverflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(bookOverflow).toBeLessThanOrEqual(1);
  const bookResults = await new AxeBuilder({ page }).analyze();
  const seriousBookIssues = bookResults.violations.filter((violation) => ["serious", "critical"].includes(violation.impact));
  expect(seriousBookIssues).toEqual([]);

  await page.goto("tests/?module=module-01");
  await expect(page.getByRole("heading", { name: "Python and pandas foundations" })).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);
  const results = await new AxeBuilder({ page }).analyze();
  const serious = results.violations.filter((violation) => ["serious", "critical"].includes(violation.impact));
  expect(serious).toEqual([]);
});

test("explanation gating, progress restoration, and certificate work locally", async ({ browser }) => {
  const firstContext = await browser.newContext();
  const firstPage = await firstContext.newPage();
  await firstPage.goto("tests/?module=module-01");
  const moduleOne = quiz.modules.find((item) => item.module_id === "module-01");
  for (const question of moduleOne.questions) await fillQuestion(firstPage, question, wrongValue(question));
  await firstPage.getByRole("button", { name: "Grade completed attempt" }).click();
  await expect(firstPage.locator("#grade-summary")).toContainText("Not passed yet");
  await expect(firstPage.locator("#feedback-m1_q01")).toContainText("remain hidden");
  await firstPage.getByRole("button", { name: "Grade completed attempt" }).click();
  await expect(firstPage.locator("#feedback-m1_q01")).toContainText("Correct answer");

  const restored = {
    schema_version: 1,
    modules: Object.fromEntries(quiz.modules.map((item, index) => [
      item.module_id,
      { attempts: 1, best_score: 80 + index, passed: true, completed_at: `2026-08-2${index + 1}T12:00:00.000Z` },
    ])),
    exported_at: new Date().toISOString(),
  };
  await firstContext.close();

  const secondContext = await browser.newContext();
  const secondPage = await secondContext.newPage();
  await secondPage.goto("tests/?module=module-01");
  await secondPage.locator("#import-progress").setInputFiles({
    name: "learning-lab-progress-v1.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(restored)),
  });
  await expect(secondPage.locator("#progress-status")).toContainText("Progress imported");
  await expect(secondPage.locator("#certificate-link")).toBeVisible();
  await secondPage.locator("#certificate-link").click();
  await expect(secondPage.getByRole("heading", { name: "Local completion record" })).toBeVisible();
  await secondPage.locator("#display-name").fill("Local Learner");
  await secondPage.getByRole("button", { name: "Create local record" }).click();
  await expect(secondPage.locator("#certificate-title")).toHaveText("Self-assessed Learning Lab Completion Record");
  await expect(secondPage.locator("#certificate-name")).toHaveText("Local Learner");
  await expect(secondPage.locator("#certificate")).toContainText("not externally verified");
  await secondPage.emulateMedia({ media: "print" });
  await expect(secondPage.locator("#certificate")).toBeVisible();
  await secondContext.close();
});

test("JupyterLite executes geospatial and regression smoke cells", async ({ page }) => {
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
