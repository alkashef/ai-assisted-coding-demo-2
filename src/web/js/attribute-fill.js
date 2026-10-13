// @ts-check
/**
 * @module attribute-fill
 * Fills the extracted and calculated attributes of a candidate into a cloned template, for the
 * job view and the candidate view (RNK-003, CND-002, MIS-001). Shows "Not available" for a missing
 * value. Does not call the API and does not format values (format.js does).
 */

import { config } from "./config.js";
import {
  displayText,
  formatAverageMonths,
  formatGaps,
  formatMonths,
  formatParts,
  formatYesNo,
  isMissing,
} from "./format.js";

/**
 * Finds an element that a template must contain.
 * @param {ParentNode} root The cloned template or an element in it.
 * @param {string} selector A CSS selector.
 * @returns {HTMLElement} The element.
 */
export function part(root, selector) {
  return /** @type {HTMLElement} */ (root.querySelector(selector));
}

/**
 * Shows text in an element, in the "not available" style when the value is missing (MIS-001).
 * @param {HTMLElement} element The element to fill.
 * @param {string} text The text to show.
 * @param {boolean} missing True when the API gave no value.
 * @returns {void}
 */
export function setText(element, text, missing) {
  element.textContent = text;
  element.classList.toggle("not-available", missing);
}

/**
 * Fills the six key values of the calculated attributes (CAL-001 to CAL-005, CAL-007).
 * @param {ParentNode} root The cloned template with `[data-stat]` elements.
 * @param {import("./api.js").CalculatedAttributes | null} calculated The calculated attributes.
 * @returns {void}
 */
export function fillStats(root, calculated) {
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
    setText(part(root, `[data-stat='${name}']`), String(text), isMissing(value));
  }
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
 * Fills the extracted attributes (EXT-002 to EXT-010, except the name and the last job).
 * @param {ParentNode} root The cloned template with `[data-fact]` elements.
 * @param {import("./api.js").ExtractedAttributes | null} extracted The extracted attributes.
 * @returns {void}
 */
export function fillFacts(root, extracted) {
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
    setText(part(root, `[data-fact='${name}']`), text, text === config.notAvailableText);
  }
  fillSkills(part(root, "[data-fact='skills']"), e.skills ?? []);
}
