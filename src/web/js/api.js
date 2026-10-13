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
 * @typedef {{ title: string | null, employer: string | null, city: string | null,
 *   country: string | null, start: string, end: string | null,
 *   description: string | null }} LastJob
 * @typedef {{ name: string | null, current_title: string | null, skills: string[],
 *   city: string | null, country: string | null, highest_degree: string | null,
 *   countries: string[], employers: string[], last_job: LastJob | null }} ExtractedAttributes
 * @typedef {{ total_months: number | null, job_count: number | null,
 *   average_job_months: number | null, gaps: number[] | null,
 *   months_since_graduation: number | null,
 *   currently_employed: boolean | null }} CalculatedAttributes
 * @typedef {{ interview: boolean, reason: string }} Recommendation
 * @typedef {{ candidate_id: string, score: number | null,
 *   recommendation: Recommendation | null, extracted: ExtractedAttributes | null,
 *   calculated: CalculatedAttributes | null }} RankedCandidate
 * @typedef {{ candidate_id: string, text: string, extracted: ExtractedAttributes | null,
 *   calculated: CalculatedAttributes | null }} CandidateDetail
 * @typedef {{ job_id: string, title: string, score: number | null }} RankedJob
 */

/**
 * Gets one JSON document.
 * @param {string} path The API path.
 * @param {boolean} [nullOnNotFound] Answer `null` for a 404 instead of failing.
 * @returns {Promise<unknown>} The parsed JSON, or `null` for an accepted 404.
 */
async function getJson(path, nullOnNotFound = false) {
  try {
    const response = await fetch(path);
    if (nullOnNotFound && response.status === 404) {
      return null;
    }
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

/**
 * Gets every candidate for a job description, best match first (JOB-002, RNK-003, REC-001).
 * @param {string} jobId The job description ID.
 * @returns {Promise<RankedCandidate[]>} The ranked candidates with their attributes.
 */
async function listRankedCandidates(jobId) {
  const path = `${config.api.jobs}/${encodeURIComponent(jobId)}/ranked-candidates`;
  return /** @type {RankedCandidate[]} */ (await getJson(path));
}

/**
 * Gets the raw CV text and the attributes of one candidate (CND-001, CND-002).
 * @param {string} candidateId The candidate ID.
 * @returns {Promise<CandidateDetail | null>} The candidate, or `null` when the ID is unknown.
 */
async function getCandidate(candidateId) {
  const path = `${config.api.candidates}/${encodeURIComponent(candidateId)}`;
  return /** @type {CandidateDetail | null} */ (await getJson(path, true));
}

/**
 * Gets every job description for a candidate, best match first (CND-003).
 * @param {string} candidateId The candidate ID.
 * @returns {Promise<RankedJob[]>} The ranked job descriptions with their scores.
 */
async function listRankedJobs(candidateId) {
  const path = `${config.api.candidates}/${encodeURIComponent(candidateId)}/ranked-jobs`;
  return /** @type {RankedJob[]} */ (await getJson(path));
}

/** The reads that the views need. Pass it into the code that uses it, so tests can use a fake. */
export const api = Object.freeze({
  listJobs,
  listCandidates,
  listFailures,
  listRankedCandidates,
  getCandidate,
  listRankedJobs,
});
