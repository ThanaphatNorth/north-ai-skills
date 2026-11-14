---
title: formatPrice drops the second decimal
type: bug
status: todo
labels:
priority: high
rank: 1
created: 2026-11-11 10:00
updated: 2026-11-11 10:00
links:
---

## Description
Prices show one decimal place. Every customer sees it on the product page.

## Steps to reproduce
1. Call `formatPrice(1999)`.

## Expected
`$19.99`. It returns `$20.0`.

## Comments
### c1 · 2026-11-11 10:05 · Mali (QA)
Also seen with 500: it shows `$5.0`, expected `$5.00`.
