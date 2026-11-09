import { listOrders } from "../application/listOrders.js";

/** HTTP handlers for orders. Ports come in from the composition root. */
export const orderRoutes = ({ orders }) => ({
  "GET /orders": () => ({ status: 200, body: listOrders(orders) }),
});
