// @ts-check
import assert from "node:assert/strict";
import { test } from "node:test";

import {
  displayText,
  formatAverageMonths,
  formatGaps,
  formatLastJob,
  formatMonths,
  formatParts,
  formatScore,
  formatYesNo,
} from "../../src/web/js/format.js";

test("test_mis_001_null_renders_as_not_available", () => {
  assert.equal(displayText(null), "Not available");
  assert.equal(displayText(undefined), "Not available");
  assert.equal(formatMonths(null), "Not available");
  assert.equal(formatAverageMonths(null), "Not available");
  assert.equal(formatGaps(null), "Not available");
});

test("test_mis_001_a_present_value_renders_as_its_text", () => {
  assert.equal(displayText("Ada Invented"), "Ada Invented");
  assert.equal(displayText(0), "0");
});

test("test_cal_004_gaps_render_as_none_or_a_count_and_months", () => {
  assert.equal(formatGaps([]), "None");
  assert.equal(formatGaps([1]), "1 gap: 1 month");
  assert.equal(formatGaps([3]), "1 gap: 3 months");
  assert.equal(formatGaps([2, 5]), "2 gaps: 2, 5 months");
});

test("test_cal_003_months_render_with_one_decimal_for_the_average", () => {
  assert.equal(formatAverageMonths(5.456), "5.5 months");
  assert.equal(formatAverageMonths(6), "6.0 months");
});

test("test_cal_001_months_render_as_a_whole_number_with_a_unit", () => {
  assert.equal(formatMonths(106), "106 months");
  assert.equal(formatMonths(1), "1 month");
  assert.equal(formatMonths(0), "0 months");
});

test("test_rnk_003_score_renders_with_two_decimals", () => {
  assert.equal(formatScore(0.7123), "0.71");
  assert.equal(formatScore(null), "Not available");
});

test("test_cal_007_currently_employed_renders_yes_or_no", () => {
  assert.equal(formatYesNo(true), "Yes");
  assert.equal(formatYesNo(false), "No");
  assert.equal(formatYesNo(null), "Not available");
});

test("test_mis_001_parts_skip_missing_values", () => {
  assert.equal(formatParts(["Boston", null, "United States"]), "Boston, United States");
  assert.equal(formatParts([null, undefined]), "Not available");
});

test("test_ext_009_last_job_renders_on_one_line", () => {
  const job = {
    title: "Analyst",
    employer: "Acme",
    city: null,
    country: "Peru",
    start: "2019-03",
    end: null,
    description: null,
  };
  assert.equal(formatLastJob(job), "Analyst at Acme, Peru. 2019-03 to Present.");
  assert.equal(formatLastJob(null), "Not available");
});
