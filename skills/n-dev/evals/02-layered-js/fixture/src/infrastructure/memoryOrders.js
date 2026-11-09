/** In-memory storage adapter for the orders port. */
export const memoryOrders = (rows = []) => ({ all: () => rows.slice() });
