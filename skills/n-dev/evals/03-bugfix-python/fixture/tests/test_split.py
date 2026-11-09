import unittest

from billing.split import split_bill


class SplitBill(unittest.TestCase):
    def test_even_split(self):
        self.assertEqual(split_bill(9000, 3), [3000, 3000, 3000])

    def test_one_person_pays_all(self):
        self.assertEqual(split_bill(4321, 1), [4321])

    def test_nobody_is_an_error(self):
        with self.assertRaises(ValueError):
            split_bill(100, 0)


if __name__ == "__main__":
    unittest.main()
