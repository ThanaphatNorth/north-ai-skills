import { test } from "node:test";
import assert from "node:assert/strict";
import { buildApp } from "../src/main.js";

const rows = [
  { id: "a", placedAt: "2026-11-01", lines: [{ price: 60000, qty: 1 }] },
  { id: "b", placedAt: "2026-11-03", lines: [{ price: 500, qty: 1 }] },
  { id: "c", placedAt: "2026-11-05", lines: [{ price: 25000, qty: 2 }] },
];

test("GET /orders/large returns orders at or over min, newest first", () => {
  const res = buildApp(rows)["GET /orders/large"]({ query: { min: "50000" } });
  assert.equal(res.status, 200);
  assert.deepEqual(res.body.map((o) => o.id), ["c", "a"]);
});
test("GET /orders/large rejects a missing or non-numeric min", () => {
  assert.equal(buildApp(rows)["GET /orders/large"]({ query: {} }).status, 400);
  assert.equal(buildApp(rows)["GET /orders/large"]({ query: { min: "lots" } }).status, 400);
});
