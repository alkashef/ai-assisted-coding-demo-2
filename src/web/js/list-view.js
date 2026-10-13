// @ts-check
/**
 * @module list-view
 * Owns the navigation lists: fills them from the API data (LST-001, LST-002), marks the current
 * item, reads the selection from the address and folds the navigation at phone width. Does not
 * call the API and does not show the selected view (job-view.js and candidate-view.js do).
 */

import { config } from "./config.js";
import { displayText, isMissing } from "./format.js";

/**
 * @typedef {{ id: string, label: string | null, href: string }} NavEntry
 */

/**
 * Builds the navigation entries of the job descriptions.
 * @param {import("./api.js").JobSummary[]} jobs The job descriptions from the API.
 * @returns {NavEntry[]} One entry per job description, linking to its view.
 */
export function jobEntries(jobs) {
  return jobs.map((job) => ({
    id: job.id,
    label: job.title,
    href: config.routes.jobs + encodeURIComponent(job.id),
  }));
}

/**
 * Builds the navigation entries of the candidates. A missing name stays `null` (MIS-001).
 * @param {import("./api.js").CandidateSummary[]} candidates The candidates from the API.
 * @returns {NavEntry[]} One entry per candidate, linking to the candidate view.
 */
export function candidateEntries(candidates) {
  return candidates.map((candidate) => ({
    id: candidate.id,
    label: candidate.name,
    href: config.routes.candidates + encodeURIComponent(candidate.id),
  }));
}

/**
 * Reads the selected item from the address hash.
 * @param {string} hash The address hash, such as "#/jobs/j1.txt".
 * @returns {{ kind: "jobs" | "candidates", id: string } | null} The selection, or `null` when
 *   the hash names none.
 */
export function parseRoute(hash) {
  for (const kind of /** @type {const} */ (["jobs", "candidates"])) {
    const prefix = config.routes[kind];
    if (hash.startsWith(prefix) && hash.length > prefix.length) {
      return { kind, id: decodeURIComponent(hash.slice(prefix.length)) };
    }
  }
  return null;
}

/**
 * Clones the item template and fills it with one entry.
 * @param {HTMLTemplateElement} template The navigation item template.
 * @param {NavEntry} entry The entry to show.
 * @returns {DocumentFragment} The filled item.
 */
function buildItem(template, entry) {
  const item = /** @type {DocumentFragment} */ (template.content.cloneNode(true));
  const link = /** @type {HTMLAnchorElement} */ (item.querySelector(".nav-link"));
  const label = /** @type {HTMLElement} */ (item.querySelector(".nav-label"));
  const id = /** @type {HTMLElement} */ (item.querySelector(".nav-id"));
  link.setAttribute("href", entry.href);
  label.textContent = displayText(entry.label);
  label.classList.toggle("not-available", isMissing(entry.label));
  id.textContent = entry.id;
  return item;
}

/**
 * Fills one navigation group with its entries and shows how many there are.
 * @param {HTMLElement} group The group element that holds `[data-list]` and `[data-count]`.
 * @param {HTMLTemplateElement} template The navigation item template.
 * @param {NavEntry[]} entries The entries to show.
 * @returns {void}
 */
export function renderList(group, template, entries) {
  const list = /** @type {HTMLElement} */ (group.querySelector("[data-list]"));
  const count = /** @type {HTMLElement} */ (group.querySelector("[data-count]"));
  count.textContent = `(${entries.length})`;
  list.replaceChildren(...entries.map((entry) => buildItem(template, entry)));
}

/**
 * Highlights the item whose link matches the address, and clears the others.
 * @param {HTMLElement} nav The navigation element.
 * @param {string} hash The current address hash, such as "#/jobs/j1.txt".
 * @returns {void}
 */
export function markCurrent(nav, hash) {
  for (const link of nav.querySelectorAll(".nav-link")) {
    const current = link.getAttribute("href") === hash;
    link.classList.toggle("nav-link-current", current);
    if (current) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  }
}

/**
 * Closes the navigation fold at phone width, so the results come first, and opens it otherwise.
 * @param {HTMLDetailsElement} fold The navigation fold.
 * @param {string} phoneQuery The media query for phone width.
 * @returns {void}
 */
export function foldOnPhone(fold, phoneQuery) {
  const phone = window.matchMedia(phoneQuery);
  fold.open = !phone.matches;
  phone.addEventListener("change", (event) => {
    fold.open = !event.matches;
  });
}
