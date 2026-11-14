import { listOrders } from "../application/listOrders.js";

export function orderRoutes(repo) {
  return { "GET /orders": () => ({ status: 200, body: listOrders(repo) }) };
}
