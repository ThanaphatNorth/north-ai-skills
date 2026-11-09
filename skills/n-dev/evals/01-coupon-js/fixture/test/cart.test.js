import { test } from "node:test";
import assert from "node:assert/strict";
import { subtotal } from "../src/cart.js";

test("subtotal sums price times quantity", () => {
  assert.equal(subtotal({ items: [{ price: 1000, qty: 2 }, { price: 250, qty: 1 }] }), 2250);
});
