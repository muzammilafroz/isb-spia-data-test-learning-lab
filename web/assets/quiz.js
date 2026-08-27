import {
  STORAGE_KEY,
  canReveal,
  certificateEligible,
  emptyProgress,
  gradeModule,
  recordAttempt,
  validateProgress,
} from "./quiz-core.mjs";

const elements = {
  nav: document.querySelector("#module-nav"),
  form: document.querySelector("#quiz-form"),
  title: document.querySelector("#test-title"),
  meta: document.querySelector("#test-meta"),
  grade: document.querySelector("#grade-button"),
  summary: document.querySelector("#grade-summary"),
  bundle: document.querySelector("#bundle-json"),
  bundleButton: document.querySelector("#paste-bundle"),
  bundleStatus: document.querySelector("#bundle-status"),
  progressTable: document.querySelector("#progress-table"),
  progressStatus: document.querySelector("#progress-status"),
  exportButton: document.querySelector("#export-progress"),
  importInput: document.querySelector("#import-progress"),
  certificate: document.querySelector("#certificate-link"),
};

let spec;
let module;
let progress;

function loadProgress(moduleIds) {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return emptyProgress();
  try {
    return validateProgress(JSON.parse(raw), moduleIds);
  } catch (error) {
    elements.progressStatus.textContent = `Stored progress was invalid and was ignored: ${error.message}`;
    return emptyProgress();
  }
}

function saveProgress() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
}

function selectedModuleId() {
  const requested = new URLSearchParams(window.location.search).get("module");
  return spec.modules.some((item) => item.module_id === requested) ? requested : spec.modules[0].module_id;
}

function renderNav() {
  elements.nav.innerHTML = "";
  for (const item of spec.modules) {
    const link = document.createElement("a");
    link.href = `?module=${encodeURIComponent(item.module_id)}`;
    link.textContent = item.title;
    if (item.module_id === module.module_id) link.setAttribute("aria-current", "page");
    elements.nav.append(link);
  }
}

function inputFor(question) {
  const wrapper = document.createElement("div");
  if (question.type === "multiple-choice" || question.type === "multi-select") {
    for (const choice of question.choices) {
      const label = document.createElement("label");
      label.className = "choice";
      const input = document.createElement("input");
      input.type = question.type === "multi-select" ? "checkbox" : "radio";
      input.name = question.question_id;
      input.value = choice.value;
      label.append(input, document.createTextNode(choice.label));
      wrapper.append(label);
    }
  } else {
    const label = document.createElement("label");
    label.htmlFor = `answer-${question.question_id}`;
    label.textContent = question.type === "float" ? "Numeric answer" : "Answer";
    const input = document.createElement("input");
    input.id = `answer-${question.question_id}`;
    input.name = question.question_id;
    input.type = ["integer", "float"].includes(question.type) ? "number" : "text";
    if (question.type === "float") input.step = "any";
    label.append(input);
    wrapper.append(label);
  }
  return wrapper;
}

function renderQuiz() {
  elements.title.textContent = module.title;
  const record = progress.modules[module.module_id];
  elements.meta.textContent = `${module.questions.length} questions. Completed attempts: ${record?.attempts ?? 0}. Best score: ${record?.best_score ?? 0}%.`;
  elements.form.innerHTML = "";
  module.questions.forEach((question, index) => {
    const section = document.createElement("section");
    section.className = "question";
    section.id = `question-${question.question_id}`;
    const heading = document.createElement("h3");
    heading.textContent = `${index + 1}. ${question.prompt}`;
    const id = document.createElement("p");
    id.className = "small";
    id.textContent = `Question ID: ${question.question_id}`;
    const feedback = document.createElement("div");
    feedback.id = `feedback-${question.question_id}`;
    feedback.className = "feedback hidden";
    section.append(heading, id, inputFor(question), feedback);
    elements.form.append(section);
  });
  elements.summary.textContent = "Complete every answer before grading. Correct answers and explanations appear after a pass or after your second completed attempt.";
}

function readAnswers() {
  const answers = {};
  for (const question of module.questions) {
    if (question.type === "multi-select") {
      answers[question.question_id] = [...elements.form.querySelectorAll(`input[name="${question.question_id}"]:checked`)].map((input) => input.value);
    } else if (question.type === "multiple-choice") {
      answers[question.question_id] = elements.form.querySelector(`input[name="${question.question_id}"]:checked`)?.value ?? "";
    } else {
      answers[question.question_id] = elements.form.querySelector(`[name="${question.question_id}"]`).value;
    }
  }
  return answers;
}

function writeAnswer(question, value) {
  if (question.type === "multi-select") {
    const selected = Array.isArray(value) ? value.map(String) : String(value ?? "").split(",").map((item) => item.trim());
    elements.form.querySelectorAll(`input[name="${question.question_id}"]`).forEach((input) => {
      input.checked = selected.includes(input.value);
    });
  } else if (question.type === "multiple-choice") {
    elements.form.querySelectorAll(`input[name="${question.question_id}"]`).forEach((input) => {
      input.checked = String(value) === input.value;
    });
  } else {
    elements.form.querySelector(`[name="${question.question_id}"]`).value = value ?? "";
  }
}

function formatCorrectAnswer(question) {
  if (Array.isArray(question.answer)) return question.answer.join(", ");
  return String(question.answer);
}

function renderGrade(grade, reveal) {
  const lookup = new Map(grade.results.map((result) => [result.question_id, result.correct]));
  for (const question of module.questions) {
    const correct = lookup.get(question.question_id);
    const feedback = document.querySelector(`#feedback-${question.question_id}`);
    feedback.className = `feedback ${correct ? "correct" : "incorrect"}`;
    if (reveal) {
      feedback.textContent = `${correct ? "Correct." : `Incorrect. Correct answer: ${formatCorrectAnswer(question)}.`} ${question.explanation}`;
    } else {
      feedback.textContent = correct ? "Correct." : "Incorrect. The answer and explanation remain hidden until you pass or complete a second attempt.";
    }
  }
  elements.summary.className = `panel status ${grade.passed ? "good" : "bad"}`;
  elements.summary.textContent = `${grade.correct} of ${grade.total} correct: ${grade.score}%. ${grade.passed ? "Passed." : "Not passed yet."} ${reveal ? "Full explanations are now visible." : "Complete another attempt to reveal explanations."}`;
}

function renderProgress() {
  const rows = spec.modules.map((item) => {
    const record = progress.modules[item.module_id] ?? { attempts: 0, best_score: 0, passed: false };
    return `<tr><th scope="row">${item.title}</th><td>${record.attempts}</td><td>${record.best_score}%</td><td>${record.passed ? "Passed" : "Not yet"}</td></tr>`;
  }).join("");
  elements.progressTable.innerHTML = `<table><thead><tr><th>Assessment</th><th>Attempts</th><th>Best</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table>`;
  const eligible = certificateEligible(progress, spec.modules.map((item) => item.module_id));
  elements.certificate.classList.toggle("hidden", !eligible);
}

elements.grade.addEventListener("click", () => {
  const answers = readAnswers();
  const grade = gradeModule(module, answers, spec.pass_percent);
  if (!grade.complete) {
    elements.summary.className = "panel status bad";
    elements.summary.textContent = `This attempt was not counted. Complete: ${grade.missing.join(", ")}.`;
    document.querySelector(`#question-${grade.missing[0]}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
    return;
  }
  progress = recordAttempt(progress, module.module_id, grade, new Date().toISOString());
  saveProgress();
  const attempts = progress.modules[module.module_id].attempts;
  renderGrade(grade, canReveal(grade.passed, attempts));
  renderProgress();
  elements.meta.textContent = `${module.questions.length} questions. Completed attempts: ${attempts}. Best score: ${progress.modules[module.module_id].best_score}%.`;
});

elements.bundleButton.addEventListener("click", () => {
  try {
    const bundle = JSON.parse(elements.bundle.value);
    if (bundle.schema_version !== 1 || bundle.module_id !== module.module_id || typeof bundle.answers !== "object") {
      throw new Error(`Bundle must use schema version 1 and module_id ${module.module_id}.`);
    }
    for (const question of module.questions) writeAnswer(question, bundle.answers[question.question_id]);
    elements.bundleStatus.className = "good";
    elements.bundleStatus.textContent = "Bundle loaded into the form. Review the fields, then grade the completed attempt.";
  } catch (error) {
    elements.bundleStatus.className = "bad";
    elements.bundleStatus.textContent = `Could not load bundle: ${error.message}`;
  }
});

elements.exportButton.addEventListener("click", () => {
  const exported = { ...progress, exported_at: new Date().toISOString() };
  const blob = new Blob([`${JSON.stringify(exported, null, 2)}\n`], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "learning-lab-progress-v1.json";
  link.click();
  URL.revokeObjectURL(link.href);
});

elements.importInput.addEventListener("change", async () => {
  const selectedFile = elements.importInput.files?.[0];
  if (!selectedFile) return;
  try {
    const imported = JSON.parse(await selectedFile.text());
    progress = validateProgress(imported, spec.modules.map((item) => item.module_id));
    saveProgress();
    renderProgress();
    renderQuiz();
    elements.progressStatus.className = "good";
    elements.progressStatus.textContent = "Progress imported into this browser.";
  } catch (error) {
    elements.progressStatus.className = "bad";
    elements.progressStatus.textContent = `Import failed: ${error.message}`;
  } finally {
    elements.importInput.value = "";
  }
});

async function start() {
  const response = await fetch("../assets/quiz-spec.v1.json");
  if (!response.ok) throw new Error(`Quiz specification failed to load: HTTP ${response.status}`);
  spec = await response.json();
  progress = loadProgress(spec.modules.map((item) => item.module_id));
  module = spec.modules.find((item) => item.module_id === selectedModuleId());
  renderNav();
  renderQuiz();
  renderProgress();
}

start().catch((error) => {
  elements.summary.className = "panel status bad";
  elements.summary.textContent = error.message;
});
