"""Stock levels. An item is {"sku": str, "qty": int}."""


def total_units(items: list) -> int:
    return sum(item["qty"] for item in items)
