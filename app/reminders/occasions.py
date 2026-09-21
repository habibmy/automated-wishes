from dataclasses import dataclass
from datetime import date

from app.contacts.models import Contact
from app.reminders.dates import next_occurrence


@dataclass(frozen=True)
class Occasion:
    contact_uid: str
    contact_name: str
    kind: str
    original_date: date
    next_date: date

    def days_until(self, today: date) -> int:
        return (self.next_date - today).days


def get_upcoming_occasions(
    contact: Contact,
    today: date,
) -> list[Occasion]:
    occasions: list[Occasion] = []

    if contact.birthday is not None:
        occasions.append(
            Occasion(
                contact_uid=contact.uid,
                contact_name=contact.name,
                kind="birthday",
                original_date=contact.birthday,
                next_date=next_occurrence(
                    contact.birthday.month,
                    contact.birthday.day,
                    today,
                ),
            )
        )

    if contact.anniversary is not None:
        occasions.append(
            Occasion(
                contact_uid=contact.uid,
                contact_name=contact.name,
                kind="anniversary",
                original_date=contact.anniversary,
                next_date=next_occurrence(
                    contact.anniversary.month,
                    contact.anniversary.day,
                    today,
                ),
            )
        )

    return occasions