import { memoryOrders } from "./infrastructure/memoryOrders.js";
import { orderRoutes } from "./interface/orderRoutes.js";

/** Composition root: builds adapters and the route table. */
export const buildApp = (rows = []) => {
  const orders = memoryOrders(rows);
  return { ...orderRoutes({ orders }) };
};
