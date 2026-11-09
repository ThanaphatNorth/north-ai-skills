import { test } from "node:test";
import assert from "node:assert/strict";
import { signup } from "../src/signup.js";

const store = () => { const rows = []; return { rows, add: (u) => rows.push(u) }; };

test("signup stores a valid user", () => {
  const users = store();
  assert.deepEqual(signup({ email: "a@b.co", mobile: "0812345678" }, users), { user: { email: "a@b.co", mobile: "0812345678" } });
  assert.equal(users.rows.length, 1);
});
test("signup rejects a bad mobile", () => {
  assert.deepEqual(signup({ email: "a@b.co", mobile: "123" }, store()), { error: "invalid_mobile" });
});
