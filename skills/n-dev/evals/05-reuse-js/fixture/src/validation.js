/** Shared input checks. Each returns true when the value is acceptable. */
export const isEmail = (value) => typeof value === "string" && /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value);
export const isThaiMobile = (value) => typeof value === "string" && /^0[689]\d{8}$/.test(value);
