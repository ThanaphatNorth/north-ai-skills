import unittest
from datetime import date

from inventory.report import report_title


class ReportTitle(unittest.TestCase):
    def test_title_uses_thai_day_month_year(self):
        # Owned by the reporting team (ticket REP-112, open): the title format is still being agreed.
        self.assertEqual(report_title(date(2026, 11, 9)), "Stock report 09/11/2026")


if __name__ == "__main__":
    unittest.main()
