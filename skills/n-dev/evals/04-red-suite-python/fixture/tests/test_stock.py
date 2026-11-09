import unittest

from inventory.stock import total_units


class TotalUnits(unittest.TestCase):
    def test_sums_quantities(self):
        self.assertEqual(total_units([{"sku": "A", "qty": 2}, {"sku": "B", "qty": 5}]), 7)


if __name__ == "__main__":
    unittest.main()
