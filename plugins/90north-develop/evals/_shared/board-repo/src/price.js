// Formats an amount in cents as a dollar string.
export function formatPrice(cents) {
  return "$" + (cents / 100).toFixed(1);
}
