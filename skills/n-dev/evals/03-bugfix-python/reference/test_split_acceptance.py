import unittest

from billing.split import split_bill


class SplitAcceptance(unittest.TestCase):
    def test_shares_always_add_up_and_differ_by_at_most_one_satang(self):
        for total in (0, 1, 2, 99, 100, 10000, 12345, 99999):
            for people in range(1, 8):
                shares = split_bill(total, people)
                self.assertEqual((len(shares), sum(shares)), (people, total), (total, people))
                self.assertLessEqual(max(shares) - min(shares), 1, (total, people))

    def test_the_extra_satang_goes_to_the_first_people(self):
        self.assertEqual(split_bill(10000, 3), [3334, 3333, 3333])
        self.assertEqual(split_bill(10001, 3), [3334, 3334, 3333])


if __name__ == "__main__":
    unittest.main()
