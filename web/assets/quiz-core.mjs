export const STORAGE_KEY = "applied-data-coding-learning-lab-progress-v1";

export function normalizeString(value) {
  return String(value ?? "").trim().replace(/\s+/g, " ").toLowerCase();
}

function asSelection(value) {
  if (Array.isArray(value)) return value;
  if (value === null || value === undefined || value === "") return [];
  return String(value).split(",");
}

export function answerIsPresent(question, value) {
  if (question.type === "multi-select") return asSelection(value).length > 0;
  return value !== null && value !== undefined && String(value).trim() !== "";
}

export function scoreAnswer(question, value) {
  if (!answerIsPresent(question, value)) return false;
  if (question.type === "integer") {
    const observed = Number(value);
    return Number.isInteger(observed) && observed === Number(question.answer);
  }
  if (question.type === "float") {
    const observed = Number(value);
    const expected = Number(question.answer);
    if (!Number.isFinite(observed)) return false;
    const absolute = question.tolerance?.absolute ?? 0;
    const relative = question.tolerance?.relative ?? 0;
    const allowed = Math.max(absolute, Math.abs(expected) * relative);
    return Math.abs(observed - expected) <= allowed;
  }
  if (question.type === "multi-select") {
    const observed = [...new Set(asSelection(value).map(normalizeString))].sort();
    const expected = [...new Set(question.answer.map(normalizeString))].sort();
    return observed.length === expected.length && observed.every((item, index) => item === expected[index]);
  }
  return normalizeString(value) === normalizeString(question.answer);
}

export function gradeModule(module, answers, passPercent = 80) {
  const missing = module.questions
    .filter((question) => !answerIsPresent(question, answers[question.question_id]))
    .map((question) => question.question_id);
  if (missing.length) return { complete: false, missing };

  const results = module.questions.map((question) => ({
    question_id: question.question_id,
    correct: scoreAnswer(question, answers[question.question_id]),
  }));
  const correct = results.filter((result) => result.correct).length;
  const score = Math.round((10000 * correct) / module.questions.length) / 100;
  return {
    complete: true,
    correct,
    total: module.questions.length,
    score,
    passed: score >= passPercent,
    results,
  };
}

export function canReveal(passed, completedAttempts) {
  return Boolean(passed) || Number(completedAttempts) >= 2;
}

export function emptyProgress() {
  return { schema_version: 1, modules: {}, exported_at: null };
}

export function validateProgress(value, knownModuleIds) {
  if (!value || value.schema_version !== 1 || typeof value.modules !== "object") {
    throw new Error("Progress JSON does not use schema version 1.");
  }
  const cleaned = emptyProgress();
  for (const [moduleId, record] of Object.entries(value.modules)) {
    if (!knownModuleIds.includes(moduleId)) continue;
    const attempts = Math.max(0, Number.parseInt(record.attempts ?? 0, 10) || 0);
    const bestScore = Math.min(100, Math.max(0, Number(record.best_score ?? 0) || 0));
    cleaned.modules[moduleId] = {
      attempts,
      best_score: bestScore,
      passed: Boolean(record.passed) && bestScore >= 80,
      completed_at: record.completed_at ? String(record.completed_at) : null,
    };
  }
  return cleaned;
}

export function certificateEligible(progress, requiredModuleIds) {
  return requiredModuleIds.every((moduleId) => progress.modules[moduleId]?.passed === true);
}

export function recordAttempt(progress, moduleId, grade, timestamp) {
  const previous = progress.modules[moduleId] ?? { attempts: 0, best_score: 0, passed: false, completed_at: null };
  const passed = previous.passed || grade.passed;
  return {
    ...progress,
    modules: {
      ...progress.modules,
      [moduleId]: {
        attempts: previous.attempts + 1,
        best_score: Math.max(previous.best_score, grade.score),
        passed,
        completed_at: passed ? (previous.completed_at ?? timestamp) : null,
      },
    },
  };
}
