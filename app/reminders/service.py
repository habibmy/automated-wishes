from datetime import date

from app.contacts.models import Contact
from app.reminders.occasions import Occasion, get_upcoming_occasions


def upcoming_occasions(
    contacts: list[Contact],
    today: date,
    within_days: int | None = None,
) -> list[Occasion]:
    occasions: list[Occasion] = []

    for contact in contacts:
        occasions.extend(
            get_upcoming_occasions(contact, today)
        )

    occasions.sort(
        key=lambda occasion: (
            occasion.days_until(today),
            occasion.contact_name.lower(),
        )
    )

    if within_days is not None:
        occasions = [
            occasion
            for occasion in occasions
            if occasion.days_until(today) <= within_days
        ]

    return occasions