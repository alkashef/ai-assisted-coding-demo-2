// @ts-check
/**
 * @module main
 * The entry point of the page. Connects api.js, the views and log.js, and handles unexpected
 * errors. Holds no other logic.
 */

import { api } from "./api.js";
import { config } from "./config.js";
import { renderFailures, showCrash } from "./failures-view.js";
import { candidateEntries, foldOnPhone, jobEntries, markCurrent, renderList } from "./list-view.js";
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
 * Loads the lists and the failure notice, then keeps the current item marked.
 * @returns {Promise<void>}
 */
async function start() {
  const [jobs, candidates, failures] = await Promise.all([
    api.listJobs(),
    api.listCandidates(),
    api.listFailures(),
  ]);
  const items = /** @type {HTMLTemplateElement} */ (required("#nav-item-template"));
  renderList(required("[data-group='jobs']"), items, jobEntries(jobs));
  renderList(required("[data-group='candidates']"), items, candidateEntries(candidates));
  const notice = /** @type {HTMLTemplateElement} */ (required("#failure-notice-template"));
  renderFailures(required("[data-notices]"), notice, failures);
  const nav = required("[data-nav]");
  foldOnPhone(/** @type {HTMLDetailsElement} */ (required("[data-nav-fold]")), config.phoneQuery);
  markCurrent(nav, location.hash);
  window.addEventListener("hashchange", () => markCurrent(nav, location.hash));
  logInfo(`Loaded ${jobs.length} job descriptions and ${candidates.length} candidates`);
}

window.addEventListener("error", (event) => handleCrash(event.error));
window.addEventListener("unhandledrejection", (event) => handleCrash(event.reason));
start().catch(handleCrash);
