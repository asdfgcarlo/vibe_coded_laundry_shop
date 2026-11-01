import test from "node:test";
import assert from "node:assert/strict";
import { calculateEstimate, pesos } from "../laundry/static/js/calculator.js";

test("sample service estimates and decimal arithmetic", () => {
  assert.equal(calculateEstimate(65, "5"), 325);
  assert.equal(calculateEstimate(65, "5.5"), 357.5);
  assert.equal(calculateEstimate(80, "0.5"), 40);
  assert.equal(calculateEstimate(100, "100"), 10000);
  assert.equal(calculateEstimate(65.55, "0.7"), 45.89);
  assert.match(pesos.format(325), /325\.00/);
});
test("invalid, nonfinite, out-of-range, and overprecise weights are rejected", () => {
  for (const value of [
    "",
    " ",
    "-1",
    "0",
    "0.4",
    "100.1",
    "NaN",
    "Infinity",
    "1e1",
    "1.25",
    "5kg",
  ]) {
    assert.equal(calculateEstimate(65, value), null, value);
  }
  assert.equal(calculateEstimate("bad", "5"), null);
});
