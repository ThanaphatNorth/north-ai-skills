/** Use case: every order, newest first. `orders` is the storage port: { all(): Order[] }. */
export const listOrders = (orders) => [...orders.all()].sort((a, b) => b.placedAt.localeCompare(a.placedAt));
