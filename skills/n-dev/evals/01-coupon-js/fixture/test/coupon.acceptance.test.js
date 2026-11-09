import { test } from "node:test";
import assert from "node:assert/strict";
import { checkout } from "../src/checkout.js";

const cart = (code, price = 12345) => ({ items: [{ price, qty: 1 }], couponCode: code });
const before = { now: new Date("2026-06-01T00:00:00Z") };
const after = { now: new Date("2027-01-01T00:00:00Z") };

test("SAVE10 takes 10% off the subtotal, rounded to the nearest satang", () => {
  assert.deepEqual(checkout(cart("SAVE10"), before), { subtotal: 12345, discount: 1235, total: 11110 });
});
test("SAVE10 is rejected after 2026-12-31", () => {
  assert.deepEqual(checkout(cart("SAVE10"), after), { error: "invalid_coupon" });
});
test("FLAT50 takes 5000 satang off and never goes below zero", () => {
  assert.deepEqual(checkout(cart("FLAT50", 3000), after), { subtotal: 3000, discount: 3000, total: 0 });
  assert.deepEqual(checkout(cart("FLAT50", 9000), after), { subtotal: 9000, discount: 5000, total: 4000 });
});
test("an unknown code is rejected", () => {
  assert.deepEqual(checkout(cart("FREE"), before), { error: "invalid_coupon" });
});
test("no code still charges the subtotal", () => {
  assert.deepEqual(checkout({ items: [{ price: 1000, qty: 3 }] }, before), { subtotal: 3000, discount: 0, total: 3000 });
});
