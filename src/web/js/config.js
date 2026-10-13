// @ts-check
/**
 * @module config
 * Behavior-affecting values of the front end (design section 2.2). Does not read the
 * environment: the browser has none. Holds the API paths, the visible text and the log level.
 */

export const config = Object.freeze({
  api: Object.freeze({
    jobs: "/api/jobs",
    candidates: "/api/candidates",
    failures: "/api/failures",
  }),
  routes: Object.freeze({
    jobs: "#/jobs/",
    candidates: "#/candidates/",
  }),
  notAvailableText: "Not available",
  /** Keep in step with the phone breakpoint in layout.css. */
  phoneQuery: "(max-width: 600px)",
  logLevel: "info",
});
