import assert from "node:assert/strict";
import { test } from "node:test";
import { formatPrice } from "../src/price.js";

test("formats a round amount", () => {
  assert.equal(formatPrice(500), "$5.0");
});
