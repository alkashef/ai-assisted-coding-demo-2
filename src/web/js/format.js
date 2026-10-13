// @ts-check
/**
 * @module format
 * Turns API values into display text. Pure: no DOM, no fetch. Shows "Not available" for a
 * missing value and never guesses one (MIS-001). Months and gaps follow CAL-001 to CAL-005.
 */

import { config } from "./config.js";

/**
 * Tells whether the API gave no value (`null`, MIS-001).
 * @param {unknown} value The value from the JSON.
 * @returns {boolean} True when the value is missing.
 */
export function isMissing(value) {
  return value === null || value === undefined;
}

/**
 * Returns the text to show for a value.
 * @param {string | number | null | undefined} value The value from the JSON.
 * @returns {string} The value as text, or "Not available".
 */
export function displayText(value) {
  return value === null || value === undefined ? config.notAvailableText : String(value);
}

/**
 * Formats a month count (CAL-001, CAL-005).
 * @param {number | null | undefined} months A whole number of months.
 * @returns {string} For example "106 months", or "Not available".
 */
export function formatMonths(months) {
  if (months === null || months === undefined) {
    return config.notAvailableText;
  }
  return `${months} ${months === 1 ? "month" : "months"}`;
}

/**
 * Formats the average time per job with one decimal (CAL-003).
 * @param {number | null | undefined} months The average, in months.
 * @returns {string} For example "5.5 months", or "Not available".
 */
export function formatAverageMonths(months) {
  if (months === null || months === undefined) {
    return config.notAvailableText;
  }
  return `${months.toFixed(1)} months`;
}

/**
 * Formats the employment gaps (CAL-004).
 * @param {number[] | null | undefined} gaps The length of each gap, in months.
 * @returns {string} "None", a count with the lengths such as "2 gaps: 2, 5 months", or "Not available".
 */
export function formatGaps(gaps) {
  if (gaps === null || gaps === undefined) {
    return config.notAvailableText;
  }
  if (gaps.length === 0) {
    return "None";
  }
  const count = `${gaps.length} ${gaps.length === 1 ? "gap" : "gaps"}`;
  const unit = gaps.length === 1 && gaps[0] === 1 ? "month" : "months";
  return `${count}: ${gaps.join(", ")} ${unit}`;
}
