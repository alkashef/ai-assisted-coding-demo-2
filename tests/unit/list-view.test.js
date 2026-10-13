// @ts-check
import assert from "node:assert/strict";
import { test } from "node:test";

import { isRoute } from "../../src/web/js/list-view.js";

test("isRoute matches the kind and the ID", () => {
  assert.equal(isRoute("#/jobs/x.txt", "jobs", "x.txt"), true);
  assert.equal(isRoute("#/candidates/a%20b.txt", "candidates", "a b.txt"), true);
});

test("isRoute rejects the same ID of the other kind", () => {
  assert.equal(isRoute("#/candidates/x.txt", "jobs", "x.txt"), false);
  assert.equal(isRoute("#/jobs/x.txt", "candidates", "x.txt"), false);
});

test("isRoute rejects a different ID", () => {
  assert.equal(isRoute("#/jobs/y.txt", "jobs", "x.txt"), false);
  assert.equal(isRoute("", "jobs", "x.txt"), false);
});
