// @ts-check
/**
 * @module log
 * The only module that uses `console`. Writes a message when its level reaches the level in
 * config.js. Does not format messages for the user: the views do that.
 */

import { config } from "./config.js";

/** Fixed vocabulary of log levels, lowest first. */
const LEVELS = Object.freeze({ debug: 0, info: 1, warn: 2, error: 3 });

/**
 * @typedef {keyof typeof LEVELS} Level
 */

/**
 * Writes one message to the console when the level is enabled.
 * @param {Level} level The level of the message.
 * @param {string} message The text to write.
 * @param {unknown} [detail] An error or value to write after the text.
 * @returns {void}
 */
function write(level, message, detail) {
  const threshold = LEVELS[/** @type {Level} */ (config.logLevel)];
  if (LEVELS[level] < threshold) {
    return;
  }
  const args = detail === undefined ? [message] : [message, detail];
  console[level](...args);
}

/**
 * Logs an informational message.
 * @param {string} message The text to write.
 * @returns {void}
 */
export function logInfo(message) {
  write("info", message);
}

/**
 * Logs a failure with the error that caused it.
 * @param {string} message What failed.
 * @param {unknown} cause The error, including its stack trace.
 * @returns {void}
 */
export function logError(message, cause) {
  write("error", message, cause);
}
