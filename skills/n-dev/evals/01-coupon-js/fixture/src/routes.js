import { checkout } from "./checkout.js";

export const routes = {
  "POST /checkout": (body) => checkout(body.cart),
};
