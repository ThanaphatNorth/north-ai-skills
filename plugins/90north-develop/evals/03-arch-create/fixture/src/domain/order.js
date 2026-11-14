export function total(order) {
  return order.lines.reduce((sum, line) => sum + line.qty * line.priceSatang, 0);
}
