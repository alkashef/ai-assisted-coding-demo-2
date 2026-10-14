// @ts-check
/**
 * @module candidate-view
 * Owns the candidate view: the raw CV, the extracted and calculated attributes and the job
 * descriptions ranked for one candidate (CND-001 to CND-003, MIS-001), and the not-found panel
 * for an unknown candidate. Shows no recommendation (CND-003). Fills templates with
 * `textContent`. Does not call the API (main.js passes the data in).
 */

import { fillFacts, fillStats, part, setText } from "./attribute-fill.js";
import { config } from "./config.js";
import { displayText, formatLastJob, formatScore, isMissing } from "./format.js";

/**
 * @typedef {{ view: HTMLTemplateElement, job: HTMLTemplateElement,
 *   notFound: HTMLTemplateElement }} CandidateTemplates
 */

/**
 * Builds one entry of the ranked job descriptions.
 * @param {HTMLTemplateElement} template The ranked job template.
 * @param {number} rank The position in the ranking, from 1.
 * @param {import("./api.js").RankedJob} job The ranked job description.
 * @returns {DocumentFragment} The filled entry.
 */
function buildRankedJob(template, rank, job) {
  const item = /** @type {DocumentFragment} */ (template.content.cloneNode(true));
  part(item, ".ranking-rank").textContent = String(rank);
  const title = part(item, ".ranking-title");
  title.textContent = job.title;
  title.setAttribute("href", config.routes.jobs + encodeURIComponent(job.job_id));
  setText(part(item, ".ranking-score"), formatScore(job.score), job.score === null);
  return item;
}

/**
 * Fills the head of the view: the name, the file name and the title.
 * @param {ParentNode} view The cloned view.
 * @param {import("./api.js").CandidateDetail} candidate The candidate.
 * @returns {void}
 */
function fillHead(view, candidate) {
  const extracted = candidate.extracted;
  setText(
    part(view, "[data-field='title']"),
    displayText(extracted?.name),
    isMissing(extracted?.name),
  );
  part(view, "[data-field='file']").textContent = candidate.candidate_id;
  part(view, "[data-field='meta']").textContent = displayText(extracted?.current_title);
}

/**
 * Fills the attributes panel, the last job and the raw CV text.
 * @param {ParentNode} view The cloned view.
 * @param {import("./api.js").CandidateDetail} candidate The candidate.
 * @returns {void}
 */
function fillAttributes(view, candidate) {
  fillFacts(view, candidate.extracted);
  fillStats(view, candidate.calculated);
  const lastJob = candidate.extracted?.last_job;
  setText(part(view, "[data-fact='last-job']"), formatLastJob(lastJob), !lastJob);
  part(view, "[data-field='cv-text']").textContent = candidate.text;
}

/**
 * Shows the candidate view: the attributes, the ranked job descriptions and the raw CV.
 * @param {HTMLElement} host The element that holds the view.
 * @param {CandidateTemplates} templates The templates.
 * @param {import("./api.js").CandidateDetail} candidate The selected candidate.
 * @param {import("./api.js").RankedJob[]} jobs The job descriptions, best first.
 * @returns {void}
 */
export function renderCandidateView(host, templates, candidate, jobs) {
  const view = /** @type {DocumentFragment} */ (templates.view.content.cloneNode(true));
  fillHead(view, candidate);
  fillAttributes(view, candidate);
  part(view, "[data-ranking]").replaceChildren(
    ...jobs.map((job, index) => buildRankedJob(templates.job, index + 1, job)),
  );
  host.replaceChildren(view);
}

/**
 * Shows the panel for a candidate ID that the server does not know.
 * @param {HTMLElement} host The element that holds the view.
 * @param {CandidateTemplates} templates The templates.
 * @param {string} candidateId The unknown ID from the address.
 * @returns {void}
 */
export function renderCandidateNotFound(host, templates, candidateId) {
  const panel = /** @type {DocumentFragment} */ (templates.notFound.content.cloneNode(true));
  part(panel, "[data-field='text']").textContent =
    `No candidate with ID ${candidateId} is in the CV folder. Select a candidate from the list.`;
  host.replaceChildren(panel);
}
