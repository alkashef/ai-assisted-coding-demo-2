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

/**
 * Formats a similarity score with two decimals (RNK-003).
 * @param {number | null | undefined} score The score, or `null` without a vector (MIS-002).
 * @returns {string} For example "0.71", or "Not available".
 */
export function formatScore(score) {
  return score === null || score === undefined ? config.notAvailableText : score.toFixed(2);
}

/**
 * Formats a yes-or-no value (CAL-007).
 * @param {boolean | null | undefined} value The value from the JSON.
 * @returns {string} "Yes", "No" or "Not available".
 */
export function formatYesNo(value) {
  if (value === null || value === undefined) {
    return config.notAvailableText;
  }
  return value ? "Yes" : "No";
}

/**
 * Joins the parts that exist with ", ".
 * @param {(string | null | undefined)[]} parts Text parts, some of them missing.
 * @returns {string} The joined parts, or "Not available" when none exists.
 */
export function formatParts(parts) {
  const present = parts.filter((part) => part !== null && part !== undefined && part !== "");
  return present.length === 0 ? config.notAvailableText : present.join(", ");
}

/**
 * Formats the end of a job: its month, "Present" for a current job, or "Not available" (DEC-015).
 * @param {import("./api.js").LastJob} job The job.
 * @returns {string} The end text.
 */
function formatJobEnd(job) {
  if (job.end !== null) {
    return job.end;
  }
  return job.is_current ? "Present" : config.notAvailableText;
}

/**
 * Formats the last job of a CV on one line (EXT-009).
 * @param {import("./api.js").LastJob | null | undefined} job The last job.
 * @returns {string} Title, employer, place, period and description, or "Not available".
 */
export function formatLastJob(job) {
  if (job === null || job === undefined) {
    return config.notAvailableText;
  }
  const role = [displayText(job.title), displayText(job.employer)].join(" at ");
  const place = formatParts([job.city, job.country]);
  const period = `${job.start} to ${formatJobEnd(job)}`;
  const description = job.description === null ? "" : ` ${job.description}`;
  return `${role}, ${place}. ${period}.${description}`;
}
