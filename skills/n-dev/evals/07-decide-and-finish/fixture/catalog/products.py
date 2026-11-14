"""Public product payload: the shape the storefront API returns for one product."""


def to_public(product):
    return {
        "id": product["id"],
        "name": product["name"],
        "price_cents": product["price_cents"],
    }
