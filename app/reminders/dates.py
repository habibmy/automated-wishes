from datetime import date


def next_occurrence(month: int, day: int, today: date) -> date:
    """Return the next occurrence of a month/day on or after today."""

    year = today.year

    while True:
        try:
            occurrence = date(year, month, day)
        except ValueError:
            year += 1
            continue

        if occurrence >= today:
            return occurrence

        year += 1

def days_until(month: int, day: int, today: date) -> int:
    """Return the number of days until the next occurrence."""

    occurrence = next_occurrence(month, day, today)
    return (occurrence - today).days