import vobject

from app.carddav import CardDAVResource
from app.contacts.models import Contact


def parse_contact(resource: CardDAVResource) -> Contact:
    card = vobject.readOne(resource.vcard)

    uid = str(card.uid.value)
    name = str(card.fn.value) if hasattr(card, "fn") else ""

    phones = _get_values(card, "tel")
    emails = _get_values(card, "email")

    return Contact(
        uid=uid,
        name=name,
        phones=tuple(dict.fromkeys(phones)),
        emails=tuple(dict.fromkeys(emails)),
    )


def _get_values(card, field: str) -> list[str]:
    return [
        str(entry.value)
        for entry in card.contents.get(field, [])
        if entry.value
    ]