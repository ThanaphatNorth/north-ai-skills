"""Split a bill between people. Amounts are integer satang."""


def split_bill(total: int, people: int) -> list:
    """Return one share per person."""
    if people < 1:
        raise ValueError("people must be at least 1")
    share = round(total / people)
    return [share] * people
