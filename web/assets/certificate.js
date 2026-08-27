import { STORAGE_KEY, certificateEligible, emptyProgress, validateProgress } from "./quiz-core.mjs";

const message = document.querySelector("#eligibility-message");
const namePanel = document.querySelector("#name-panel");
const nameInput = document.querySelector("#display-name");
const createButton = document.querySelector("#create-record");
const certificate = document.querySelector("#certificate");
const certificateName = document.querySelector("#certificate-name");
const scores = document.querySelector("#certificate-scores");
const completionTime = document.querySelector("#completion-time");
const printActions = document.querySelector("#print-actions");

const response = await fetch("../assets/quiz-spec.v1.json");
const spec = await response.json();
const moduleIds = spec.modules.map((item) => item.module_id);

let progress = emptyProgress();
try {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (raw) progress = validateProgress(JSON.parse(raw), moduleIds);
} catch (error) {
  message.textContent = `Stored progress could not be read: ${error.message}`;
}

if (certificateEligible(progress, moduleIds)) {
  message.className = "notice good no-print";
  message.textContent = "All six assessments are passed. Enter a display name to create the local record.";
  namePanel.classList.remove("hidden");
} else {
  message.className = "notice bad no-print";
  message.textContent = "The record is locked. Pass all five module tests and the capstone at 80 percent in this browser, or import valid progress at the test center.";
}

createButton.addEventListener("click", () => {
  const name = nameInput.value.trim();
  if (!name) {
    nameInput.focus();
    message.className = "notice bad no-print";
    message.textContent = "Enter a display name. It will remain local to this page.";
    return;
  }
  certificateName.textContent = name;
  scores.innerHTML = "";
  for (const item of spec.modules) {
    const row = document.createElement("tr");
    const title = document.createElement("th");
    title.scope = "row";
    title.textContent = item.title;
    const score = document.createElement("td");
    score.textContent = `${progress.modules[item.module_id].best_score}%`;
    row.append(title, score);
    scores.append(row);
  }
  const timestamps = moduleIds
    .map((moduleId) => progress.modules[moduleId].completed_at)
    .filter(Boolean)
    .map((value) => new Date(value));
  const completed = timestamps.length
    ? new Date(Math.max(...timestamps.map((value) => value.getTime())))
    : new Date();
  completionTime.textContent = completed.toLocaleString(undefined, { dateStyle: "long", timeStyle: "short" });
  certificate.classList.remove("hidden");
  printActions.classList.remove("hidden");
  message.textContent = "The local record is ready. The display name has not been stored or transmitted.";
});

document.querySelector("#print-record").addEventListener("click", () => window.print());
