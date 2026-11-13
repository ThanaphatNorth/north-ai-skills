import unittest

from catalog.products import to_public


class ToPublicTest(unittest.TestCase):
    def test_payload_has_exactly_the_public_fields(self):
        product = {"id": 7, "name": "Mug", "price_cents": 1200, "cost_cents": 400}
        self.assertEqual(to_public(product), {"id": 7, "name": "Mug", "price_cents": 1200})


if __name__ == "__main__":
    unittest.main()
