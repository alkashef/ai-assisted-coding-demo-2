// @ts-check
/**
 * @module job-view
 * Owns the job view: the ranked candidate cards of one job description (JOB-002, RNK-003,
 * REC-001, MIS-001, MIS-002). Fills templates with `textContent`. Does not call the API (main.js
 * passes the data in) and does not format values (format.js does).
 */

import { config } from "./config.js";
import {
  displayText,
  formatAverageMonths,
  formatGaps,
  formatLastJob,
  formatMonths,
  formatParts,
  formatScore,
  formatYesNo,
  isMissing,
} from "./format.js";

/**
 * Finds an element that a template must contain.
 * @param {ParentNode} root The cloned template or an element in it.
 * @param {string} selector A CSS selector.
 * @returns {HTMLElement} The element.
 */
function part(root, selector) {
  return /** @type {HTMLElement} */ (root.querySelector(selector));
}

/**
 * Shows text in an element, in the "not available" style when the value is missing (MIS-001).
 * @param {HTMLElement} element The element to fill.
 * @param {string} text The text to show.
 * @param {boolean} missing True when the API gave no value.
 * @returns {void}
 */
function setText(element, text, missing) {
  element.textContent = text;
  element.classList.toggle("not-available", missing);
}

/**
 * Fills the six key values of a card (CAL-001 to CAL-005, CAL-007).
 * @param {ParentNode} card The cloned card.
 * @param {import("./api.js").CalculatedAttributes | null} calculated The calculated attributes.
 * @returns {void}
 */
function fillStats(card, calculated) {
  const c = calculated ?? /** @type {Partial<import("./api.js").CalculatedAttributes>} */ ({});
  const stats = [
    ["total", c.total_months, formatMonths(c.total_months)],
    ["jobs", c.job_count, displayText(c.job_count)],
    ["average", c.average_job_months, formatAverageMonths(c.average_job_months)],
    ["gaps", c.gaps, formatGaps(c.gaps)],
    ["employed", c.currently_employed, formatYesNo(c.currently_employed)],
    ["graduation", c.months_since_graduation, formatMonths(c.months_since_graduation)],
  ];
  for (const [name, value, text] of stats) {
    setText(part(card, `[data-stat='${name}']`), String(text), isMissing(value));
  }
}

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
 * Fills the skills chips, or "Not available" when there are none.
 * @param {HTMLElement} list The chips list.
 * @param {string[]} skills The skills.
 * @returns {void}
 */
function fillSkills(list, skills) {
  const items = skills.map((skill) => {
    const item = document.createElement("li");
    item.className = "chips-item";
    item.textContent = skill;
    return item;
  });
  if (items.length === 0) {
    const none = document.createElement("li");
    none.className = "not-available";
    none.textContent = config.notAvailableText;
    items.push(none);
  }
  list.replaceChildren(...items);
}

/**
 * Fills the "More attributes" fold (EXT-002 to EXT-010).
 * @param {ParentNode} card The cloned card.
 * @param {import("./api.js").ExtractedAttributes | null} extracted The extracted attributes.
 * @returns {void}
 */
function fillFacts(card, extracted) {
  const e = extracted ?? /** @type {Partial<import("./api.js").ExtractedAttributes>} */ ({});
  const address = formatParts([e.city, e.country]);
  const countries = formatParts(e.countries ?? []);
  const companies = formatParts(e.employers ?? []);
  const facts = [
    ["title", displayText(e.current_title)],
    ["address", address],
    ["degree", displayText(e.highest_degree)],
    ["countries", countries],
    ["companies", companies],
  ];
  for (const [name, text] of facts) {
    setText(part(card, `[data-fact='${name}']`), text, text === config.notAvailableText);
  }
  fillSkills(part(card, "[data-fact='skills']"), e.skills ?? []);
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
 * Shows the job view: the job title and one card per candidate, best first.
 * @param {HTMLElement} host The element that holds the view.
 * @param {{ view: HTMLTemplateElement, card: HTMLTemplateElement }} templates The templates.
 * @param {import("./api.js").JobSummary} job The selected job description.
 * @param {import("./api.js").RankedCandidate[]} ranked The candidates, best first.
 * @returns {void}
 */
export function renderJobView(host, templates, job, ranked) {
  const view = /** @type {DocumentFragment} */ (templates.view.content.cloneNode(true));
  part(view, "[data-field='title']").textContent = job.title;
  part(view, "[data-field='meta']").textContent =
    `Job description ${job.id}. All ${ranked.length} candidates, best match first.`;
  part(view, "[data-cards]").replaceChildren(
    ...ranked.map((candidate, index) => buildCard(templates.card, index + 1, candidate)),
  );
  host.replaceChildren(view);
}
