"""Daily stock report header."""
from datetime import date


def report_title(day: date) -> str:
    return "Stock report " + day.isoformat()
