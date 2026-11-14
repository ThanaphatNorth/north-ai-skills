import { total } from "../domain/order.js";

export function listOrders(repo) {
  return repo.all().map((order) => ({ id: order.id, total: total(order) }));
}
