import { test } from "node:test";
import assert from "node:assert/strict";
import { signup } from "../src/signup.js";

const store = () => { const rows = []; return { rows, add: (u) => rows.push(u) }; };

test("signup rejects an invalid email and stores nothing", () => {
  for (const email of ["", "no-at-sign", "a@b", "a b@c.co", undefined]) {
    const users = store();
    assert.deepEqual(signup({ email, mobile: "0812345678" }, users), { error: "invalid_email" }, String(email));
    assert.equal(users.rows.length, 0);
  }
});
test("signup still accepts a valid email", () => {
  assert.ok(signup({ email: "somchai@example.co.th", mobile: "0812345678" }, store()).user);
});
