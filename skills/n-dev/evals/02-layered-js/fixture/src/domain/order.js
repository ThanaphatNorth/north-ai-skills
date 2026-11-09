/** Order total in satang. */
export const orderTotal = (order) => order.lines.reduce((sum, l) => sum + l.price * l.qty, 0);
