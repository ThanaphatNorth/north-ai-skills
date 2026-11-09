import { isThaiMobile } from "./validation.js";

/** Create an account from a sign-up form. `users` is the storage port: { add(user) }. */
export function signup(form, users) {
  if (!isThaiMobile(form.mobile)) return { error: "invalid_mobile" };
  const user = { email: form.email, mobile: form.mobile };
  users.add(user);
  return { user };
}
