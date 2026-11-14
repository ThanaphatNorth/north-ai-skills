import assert from "node:assert/strict";
import { test } from "node:test";
import { routes } from "../src/main.js";

test("lists orders with totals", () => {
  assert.deepEqual(routes["GET /orders"]().body, [{ id: 1, total: 3000 }]);
});
