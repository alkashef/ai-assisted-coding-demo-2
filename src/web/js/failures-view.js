// @ts-check
/**
 * @module failures-view
 * Owns the failure notice (ERR-001) and the on-screen crash panel for unexpected errors. Does not
 * fetch the failures and does not log (main.js connects them to api.js and log.js).
 */

/**
 * Shows the failure notice with one line per failed result, or nothing when none failed.
 * @param {HTMLElement} host The element that holds the notice.
 * @param {HTMLTemplateElement} template The failure notice template.
 * @param {import("./api.js").FailureSummary[]} failures The failures from the API.
 * @returns {void}
 */
export function renderFailures(host, template, failures) {
  host.replaceChildren();
  if (failures.length === 0) {
    return;
  }
  const notice = /** @type {DocumentFragment} */ (template.content.cloneNode(true));
  const summary = /** @type {HTMLElement} */ (notice.querySelector(".notice-summary"));
  const list = /** @type {HTMLElement} */ (notice.querySelector(".notice-list"));
  const noun = failures.length === 1 ? "result" : "results";
  summary.textContent = `${failures.length} ${noun} could not be computed`;
  list.replaceChildren(
    ...failures.map((failure) => {
      const item = document.createElement("li");
      item.textContent = `${failure.item_id}: ${failure.cause}`;
      return item;
    }),
  );
  host.append(notice);
}

/**
 * Describes an error with its stack trace and the chain of its causes.
 * @param {unknown} error The error or any thrown value.
 * @returns {string} The raw text to show.
 */
function describeError(error) {
  if (!(error instanceof Error)) {
    return String(error);
  }
  const own = error.stack ?? error.message;
  return error.cause === undefined ? own : `${own}\nCaused by: ${describeError(error.cause)}`;
}

/**
 * Shows the raw error and its stack trace on screen.
 * @param {HTMLElement} panel The crash panel that holds `[data-crash-text]`.
 * @param {unknown} error The error or any thrown value.
 * @returns {void}
 */
export function showCrash(panel, error) {
  const text = /** @type {HTMLElement} */ (panel.querySelector("[data-crash-text]"));
  text.textContent = describeError(error);
  panel.hidden = false;
}
