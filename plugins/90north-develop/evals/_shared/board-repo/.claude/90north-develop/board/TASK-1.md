---
title: Show the discount as a percent
type: story
status: todo
labels:
priority: medium
rank: 1
created: 2026-11-10 09:00
updated: 2026-11-10 09:00
links:
---

## Description
The storefront needs to show how much a sale takes off. Add a formatter beside `formatPrice`.

## Acceptance criteria
- `formatDiscount(priceCents, saleCents)` in a new file `src/discount.js` returns the percent off as a string such as `"25%"`, rounded to the nearest whole number.
- When `saleCents` is not lower than `priceCents` it returns an empty string.
- `formatPrice` and its test are unchanged.

## Comments
