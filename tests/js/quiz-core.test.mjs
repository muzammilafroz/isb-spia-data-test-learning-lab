import test from "node:test";
import assert from "node:assert/strict";

import {
  canReveal,
  certificateEligible,
  emptyProgress,
  gradeModule,
  normalizeString,
  recordAttempt,
  scoreAnswer,
  validateProgress,
} from "../../web/assets/quiz-core.mjs";

test("normalized strings ignore case and surrounding whitespace", () => {
  assert.equal(normalizeString("  EPSG:4326  "), "epsg:4326");
  assert.equal(scoreAnswer({ type: "normalized-string", answer: "Riverbend" }, " riverBEND "), true);
});

test("exact integers reject a noninteger", () => {
  assert.equal(scoreAnswer({ type: "integer", answer: 25 }, "25"), true);
  assert.equal(scoreAnswer({ type: "integer", answer: 25 }, "25.5"), false);
});

test("floating answers respect absolute and relative tolerance", () => {
  const question = { type: "float", answer: -0.15577, tolerance: { absolute: 0.001, relative: 0.001 } };
  assert.equal(scoreAnswer(question, -0.155), true);
  assert.equal(scoreAnswer(question, -0.15), false);
});

test("multi-select comparison ignores order but not extra values", () => {
  const question = { type: "multi-select", answer: ["weights", "psu", "strata"] };
  assert.equal(scoreAnswer(question, ["strata", "weights", "psu"]), true);
  assert.equal(scoreAnswer(question, ["strata", "weights", "psu", "wealth"]), false);
});

test("grading requires complete answers and accepts exactly 80 percent", () => {
  const module = {
    questions: Array.from({ length: 5 }, (_, index) => ({
      question_id: `q${index}`,
      type: "integer",
      answer: index,
    })),
  };
  assert.deepEqual(gradeModule(module, { q0: 0 }, 80), { complete: false, missing: ["q1", "q2", "q3", "q4"] });
  const grade = gradeModule(module, { q0: 0, q1: 1, q2: 2, q3: 3, q4: 99 }, 80);
  assert.equal(grade.score, 80);
  assert.equal(grade.passed, true);
});

test("explanations unlock only on pass or second completed attempt", () => {
  assert.equal(canReveal(false, 1), false);
  assert.equal(canReveal(false, 2), true);
  assert.equal(canReveal(true, 1), true);
});

test("progress import is bounded and ignores unknown modules", () => {
  const imported = validateProgress({
    schema_version: 1,
    modules: {
      known: { attempts: 2, best_score: 88, passed: true, completed_at: "2026-01-01T00:00:00Z" },
      unknown: { attempts: 99, best_score: 100, passed: true },
    },
  }, ["known"]);
  assert.deepEqual(Object.keys(imported.modules), ["known"]);
  assert.equal(imported.modules.known.passed, true);
});

test("attempt recording preserves best score and completion time", () => {
  let progress = emptyProgress();
  progress = recordAttempt(progress, "m1", { score: 70, passed: false }, "first");
  progress = recordAttempt(progress, "m1", { score: 90, passed: true }, "second");
  progress = recordAttempt(progress, "m1", { score: 80, passed: true }, "third");
  assert.equal(progress.modules.m1.attempts, 3);
  assert.equal(progress.modules.m1.best_score, 90);
  assert.equal(progress.modules.m1.completed_at, "second");
});

test("certificate requires every named module to pass", () => {
  const progress = { modules: { a: { passed: true }, b: { passed: true } } };
  assert.equal(certificateEligible(progress, ["a", "b"]), true);
  assert.equal(certificateEligible(progress, ["a", "b", "c"]), false);
});
