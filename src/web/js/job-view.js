// @ts-check
/**
 * @module job-view
 * Owns the job view: the ranked candidate cards of one job description (JOB-002, RNK-003,
 * REC-001, MIS-001, MIS-002) and its text (JOB-003). Fills templates with `textContent`. Does not
 * call the API (main.js passes the data in) and does not format values (format.js does).
 */

import { fillFacts, fillStats, part, setText } from "./attribute-fill.js";
import { config } from "./config.js";
import { displayText, formatLastJob, formatParts, formatScore, isMissing } from "./format.js";

/**
 * Fills the recommendation badge and its reason (REC-001).
 * @param {ParentNode} card The cloned card.
 * @param {import("./api.js").Recommendation | null} recommendation The recommendation, if any.
 * @returns {void}
 */
function fillRecommendation(card, recommendation) {
  const badge = part(card, ".badge");
  const reason = part(card, ".card-reason");
  badge.classList.toggle("badge-positive", recommendation?.interview === true);
  badge.classList.toggle("badge-negative", recommendation?.interview === false);
  badge.classList.toggle("badge-neutral", recommendation === null);
  if (recommendation === null) {
    setText(badge, config.notAvailableText, false);
    setText(reason, config.notAvailableText, true);
    return;
  }
  badge.textContent = recommendation.interview ? "Interview" : "Do not interview";
  reason.textContent = recommendation.reason;
}

/**
 * Fills the head of a card: rank, name, place, score and the last job.
 * @param {ParentNode} card The cloned card.
 * @param {number} rank The position in the ranking, from 1.
 * @param {import("./api.js").RankedCandidate} candidate The ranked candidate.
 * @returns {void}
 */
function fillHead(card, rank, candidate) {
  const extracted = candidate.extracted;
  const name = part(card, ".card-name a");
  setText(name, displayText(extracted?.name), isMissing(extracted?.name));
  name.setAttribute("href", config.routes.candidates + encodeURIComponent(candidate.candidate_id));
  part(card, ".card-rank").textContent = String(rank);
  part(card, ".card-sub").textContent = [
    `CV ${candidate.candidate_id}`,
    displayText(extracted?.current_title),
    formatParts([extracted?.city, extracted?.country]),
  ].join(". ");
  const score = part(card, ".card-score-value");
  setText(score, formatScore(candidate.score), candidate.score === null);
  const lastJob = part(card, "[data-field='last-job']");
  setText(lastJob, formatLastJob(extracted?.last_job), !extracted?.last_job);
}

/**
 * Builds the card of one ranked candidate.
 * @param {HTMLTemplateElement} template The candidate card template.
 * @param {number} rank The position in the ranking, from 1.
 * @param {import("./api.js").RankedCandidate} candidate The ranked candidate.
 * @returns {DocumentFragment} The filled card.
 */
function buildCard(template, rank, candidate) {
  const card = /** @type {DocumentFragment} */ (template.content.cloneNode(true));
  fillHead(card, rank, candidate);
  fillRecommendation(card, candidate.recommendation);
  fillStats(card, candidate.calculated);
  fillFacts(card, candidate.extracted);
  return card;
}

/**
 * Shows the job view: the job title, the job description text and one card per candidate, best
 * first.
 * @param {HTMLElement} host The element that holds the view.
 * @param {{ view: HTMLTemplateElement, card: HTMLTemplateElement }} templates The templates.
 * @param {import("./api.js").JobDetail} job The selected job description with its text.
 * @param {import("./api.js").RankedCandidate[]} ranked The candidates, best first.
 * @returns {void}
 */
export function renderJobView(host, templates, job, ranked) {
  const view = /** @type {DocumentFragment} */ (templates.view.content.cloneNode(true));
  part(view, "[data-field='title']").textContent = job.title;
  part(view, "[data-field='meta']").textContent =
    `Job description ${job.id}. All ${ranked.length} candidates, best match first.`;
  part(view, "[data-field='job-text']").textContent = job.text;
  part(view, "[data-cards]").replaceChildren(
    ...ranked.map((candidate, index) => buildCard(templates.card, index + 1, candidate)),
  );
  host.replaceChildren(view);
}
