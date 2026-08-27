import fs from "node:fs";
import path from "node:path";

import { chromium } from "@playwright/test";

const base = "http://127.0.0.1:8000/isb-spia-data-test-learning-lab/";
const output = path.join("tmp", "visual-review");
fs.rmSync(output, { recursive: true, force: true });
fs.mkdirSync(output, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });

await page.goto(base);
await page.screenshot({ path: path.join(output, "course-home-desktop.png"), fullPage: true });

await page.setViewportSize({ width: 390, height: 844 });
await page.goto(`${base}tests/?module=module-03`);
await page.screenshot({ path: path.join(output, "test-center-mobile.png"), fullPage: true });

const quiz = await page.evaluate(async () => (await fetch("../assets/quiz-spec.v1.json")).json());
const completedAt = "2026-08-27T12:00:00.000Z";
const progress = {
  schema_version: 1,
  modules: Object.fromEntries(quiz.modules.map((item, index) => [
    item.module_id,
    { attempts: 1, best_score: 90 + index, passed: true, completed_at: completedAt },
  ])),
  exported_at: completedAt,
};
await page.evaluate((value) => {
  localStorage.setItem("applied-data-coding-learning-lab-progress-v1", JSON.stringify(value));
}, progress);
await page.setViewportSize({ width: 1100, height: 850 });
await page.goto(`${base}certificate/`);
await page.locator("#display-name").fill("Local Learner");
await page.getByRole("button", { name: "Create local record" }).click();
await page.screenshot({ path: path.join(output, "completion-record.png"), fullPage: true });

await browser.close();
console.log(`Visual-review screenshots saved in ${output}`);
