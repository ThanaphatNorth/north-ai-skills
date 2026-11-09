import unittest

from inventory.stock import low_stock


class LowStockAcceptance(unittest.TestCase):
    def test_skus_below_threshold_sorted(self):
        items = [{"sku": "C", "qty": 1}, {"sku": "A", "qty": 0}, {"sku": "B", "qty": 9}, {"sku": "D", "qty": 3}]
        self.assertEqual(low_stock(items, 3), ["A", "C"])

    def test_nothing_low(self):
        self.assertEqual(low_stock([{"sku": "A", "qty": 5}], 3), [])


if __name__ == "__main__":
    unittest.main()
