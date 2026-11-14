import { memoryOrders } from "../infrastructure/memoryOrders.js";

export function health() {
  return { status: 200, body: { orders: memoryOrders.count() } };
}
