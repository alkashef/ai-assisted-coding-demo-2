// @ts-check
/**
 * @module main
 * The entry point of the page. Connects api.js, the views and log.js, and handles unexpected
 * errors. Holds no other logic.
 */

import { api } from "./api.js";
import { config } from "./config.js";
import { renderCandidateNotFound, renderCandidateView } from "./candidate-view.js";
import { renderFailures, showCrash } from "./failures-view.js";
import { renderJobView } from "./job-view.js";
import {
  candidateEntries,
  foldOnPhone,
  isRoute,
  jobEntries,
  markCurrent,
  parseRoute,
  renderList,
} from "./list-view.js";
import { logError, logInfo } from "./log.js";

/**
 * Finds an element that index.html must contain.
 * @param {string} selector A CSS selector.
 * @returns {HTMLElement} The element.
 */
function required(selector) {
  return /** @type {HTMLElement} */ (document.querySelector(selector));
}

/**
 * Shows an unexpected error on screen and logs it.
 * @param {unknown} error The error or any thrown value.
 * @returns {void}
 */
function handleCrash(error) {
  showCrash(required("[data-crash]"), error);
  logError("Unexpected error", error);
}

/**
 * Shows the job view of a job description, unless the address moved on while the data loaded.
 * @param {import("./api.js").JobSummary} job The selected job description.
 * @returns {Promise<void>}
 */
async function showJob(job) {
  const ranked = await api.listRankedCandidates(job.id);
  if (!isRoute(location.hash, "jobs", job.id)) {
    return;
  }
  const templates = {
    view: /** @type {HTMLTemplateElement} */ (required("#job-view-template")),
    card: /** @type {HTMLTemplateElement} */ (required("#candidate-card-template")),
  };
  renderJobView(required("[data-view]"), templates, job, ranked);
}

/**
 * Shows the candidate view, or the not-found panel for an unknown ID, unless the address moved on
 * while the data loaded.
 * @param {string} candidateId The candidate ID from the address.
 * @returns {Promise<void>}
 */
async function showCandidate(candidateId) {
  const candidate = await api.getCandidate(candidateId);
  const jobs = candidate === null ? [] : await api.listRankedJobs(candidateId);
  if (!isRoute(location.hash, "candidates", candidateId)) {
    return;
  }
  const templates = {
    view: /** @type {HTMLTemplateElement} */ (required("#candidate-view-template")),
    job: /** @type {HTMLTemplateElement} */ (required("#ranked-job-template")),
    notFound: /** @type {HTMLTemplateElement} */ (required("#candidate-not-found-template")),
  };
  const host = required("[data-view]");
  if (candidate === null) {
    renderCandidateNotFound(host, templates, candidateId);
  } else {
    renderCandidateView(host, templates, candidate, jobs);
  }
}

/**
 * Shows the view that the address names, and hides the "select an item" panel when there is one.
 * @param {import("./api.js").JobSummary[]} jobs The job descriptions, for the titles.
 * @returns {Promise<void>}
 */
async function showSelection(jobs) {
  const route = parseRoute(location.hash);
  const job = route?.kind === "jobs" ? jobs.find((item) => item.id === route.id) : undefined;
  required("[data-empty]").hidden = job !== undefined || route?.kind === "candidates";
  if (job !== undefined) {
    await showJob(job);
  } else if (route?.kind === "candidates") {
    await showCandidate(route.id);
  } else {
    required("[data-view]").replaceChildren();
  }
}

/**
 * Fills the navigation lists and starts keeping the current item marked.
 * @param {import("./api.js").JobSummary[]} jobs The job descriptions.
 * @param {import("./api.js").CandidateSummary[]} candidates The candidates.
 * @returns {void}
 */
function showNavigation(jobs, candidates) {
  const items = /** @type {HTMLTemplateElement} */ (required("#nav-item-template"));
  renderList(required("[data-group='jobs']"), items, jobEntries(jobs));
  renderList(required("[data-group='candidates']"), items, candidateEntries(candidates));
  const nav = required("[data-nav]");
  foldOnPhone(/** @type {HTMLDetailsElement} */ (required("[data-nav-fold]")), config.phoneQuery);
  markCurrent(nav, location.hash);
  window.addEventListener("hashchange", () => markCurrent(nav, location.hash));
}

/**
 * Loads the lists and the failure notice, then shows the selected view.
 * @returns {Promise<void>}
 */
async function start() {
  const [jobs, candidates, failures] = await Promise.all([
    api.listJobs(),
    api.listCandidates(),
    api.listFailures(),
  ]);
  showNavigation(jobs, candidates);
  const notice = /** @type {HTMLTemplateElement} */ (required("#failure-notice-template"));
  renderFailures(required("[data-notices]"), notice, failures);
  await showSelection(jobs);
  window.addEventListener("hashchange", () => showSelection(jobs).catch(handleCrash));
  logInfo(`Loaded ${jobs.length} job descriptions and ${candidates.length} candidates`);
}

window.addEventListener("error", (event) => handleCrash(event.error));
window.addEventListener("unhandledrejection", (event) => handleCrash(event.reason));
start().catch(handleCrash);
