import { subtotal } from "./cart.js";

/** Price a cart. Returns { subtotal, discount, total } in satang. */
export function checkout(cart, { now = new Date() } = {}) {
  const sub = subtotal(cart);
  const discount = 0;
  return { subtotal: sub, discount, total: sub - discount };
}
