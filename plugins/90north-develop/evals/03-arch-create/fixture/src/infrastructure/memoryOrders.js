const orders = [{ id: 1, lines: [{ qty: 2, priceSatang: 1500 }] }];

export const memoryOrders = { all: () => orders, count: () => orders.length };
