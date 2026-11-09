/** Sum of price × qty over the cart's items, in satang. */
export function subtotal(cart) {
  return cart.items.reduce((sum, item) => sum + item.price * item.qty, 0);
}
