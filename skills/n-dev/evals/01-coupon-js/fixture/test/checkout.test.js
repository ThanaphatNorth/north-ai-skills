import { test } from "node:test";
import assert from "node:assert/strict";
import { checkout } from "../src/checkout.js";

test("checkout without a coupon charges the subtotal", () => {
  assert.deepEqual(checkout({ items: [{ price: 1000, qty: 3 }] }), { subtotal: 3000, discount: 0, total: 3000 });
});
