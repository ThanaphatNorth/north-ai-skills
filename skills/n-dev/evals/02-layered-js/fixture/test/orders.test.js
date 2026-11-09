import { test } from "node:test";
import assert from "node:assert/strict";
import { buildApp } from "../src/main.js";

const rows = [
  { id: "a", placedAt: "2026-11-01", lines: [{ price: 1000, qty: 1 }] },
  { id: "b", placedAt: "2026-11-03", lines: [{ price: 500, qty: 1 }] },
];

test("GET /orders lists newest first", () => {
  const res = buildApp(rows)["GET /orders"]();
  assert.deepEqual(res.body.map((o) => o.id), ["b", "a"]);
});
