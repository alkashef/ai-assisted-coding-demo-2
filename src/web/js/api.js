// @ts-check
/**
 * @module api
 * The only module that calls `fetch`. Reads the JSON API (design section 4) and adds context to
 * any failure. Does not touch the DOM and does not turn values into display text.
 */

import { config } from "./config.js";

/**
 * @typedef {{ id: string, title: string }} JobSummary
 * @typedef {{ id: string, name: string | null }} CandidateSummary
 * @typedef {{ item_id: string, cause: string }} FailureSummary
 */

/**
 * Gets one JSON document.
 * @param {string} path The API path.
 * @returns {Promise<unknown>} The parsed JSON.
 */
async function getJson(path) {
  try {
    const response = await fetch(path);
    if (!response.ok) {
      throw new Error(`The server answered ${response.status}`);
    }
    return await response.json();
  } catch (cause) {
    throw new Error(`GET ${path} failed`, { cause });
  }
}

/**
 * Gets the job descriptions (LST-001).
 * @returns {Promise<JobSummary[]>} The ID and title of each job description.
 */
async function listJobs() {
  return /** @type {JobSummary[]} */ (await getJson(config.api.jobs));
}

/**
 * Gets the candidates (LST-002).
 * @returns {Promise<CandidateSummary[]>} The ID and name of each candidate.
 */
async function listCandidates() {
  return /** @type {CandidateSummary[]} */ (await getJson(config.api.candidates));
}

/**
 * Gets the failed LLM calls (ERR-001).
 * @returns {Promise<FailureSummary[]>} The item and cause of each failure.
 */
async function listFailures() {
  return /** @type {FailureSummary[]} */ (await getJson(config.api.failures));
}

/** The reads that the views need. Pass it into the code that uses it, so tests can use a fake. */
export const api = Object.freeze({ listJobs, listCandidates, listFailures });
