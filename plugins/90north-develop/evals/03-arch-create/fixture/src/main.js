import { memoryOrders } from "./infrastructure/memoryOrders.js";
import { orderRoutes } from "./interface/orderRoutes.js";

export const routes = orderRoutes(memoryOrders);
