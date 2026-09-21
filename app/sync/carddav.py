from app.carddav import CardDAVClient
from app.contacts.parser import parse_contact
from app.database.repository import ContactRepository


def sync_carddav_contacts(
    client: CardDAVClient,
    repository: ContactRepository,
) -> int:
    resources = client.fetch_contacts()

    contacts = [
        parse_contact(resource)
        for resource in resources
    ]

    repository.save_contacts(
        contacts,
        source="carddav",
    )

    return len(contacts)