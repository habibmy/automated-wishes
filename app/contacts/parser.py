from datetime import date, datetime

import vobject

from app.carddav import CardDAVResource
from app.contacts.models import Contact


def parse_contact(resource: CardDAVResource) -> Contact:
    card = vobject.readOne(resource.vcard)

    uid = str(card.uid.value)
    name = str(card.fn.value) if hasattr(card, "fn") else ""

    phones = _get_values(card, "tel")
    emails = _get_values(card, "email")

    birthday = _get_date(card, "bday")
    anniversary = _get_date(card, "anniversary")

    return Contact(
        uid=uid,
        name=name,
        phones=tuple(dict.fromkeys(phones)),
        emails=tuple(dict.fromkeys(emails)),
        birthday=birthday,
        anniversary=anniversary,
    )


def _get_values(card, field: str) -> list[str]:
    return [
        str(entry.value)
        for entry in card.contents.get(field, [])
        if entry.value
    ]


def _get_date(card, field: str) -> date | None:
    entry = card.contents.get(field, [])

    if not entry:
        return None

    value = entry[0].value

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        value = value.strip()

        for fmt in ("%Y%m%d", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue

    return None