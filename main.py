from app.carddav import CardDAVClient
from app.config import load_settings
from app.contacts.parser import parse_contact
from app.database.repository import ContactRepository

settings = load_settings()

client = CardDAVClient(
    settings.carddav_url,
    settings.carddav_username,
    settings.carddav_password,
)

resources = client.fetch_contacts()
contacts = [parse_contact(resource) for resource in resources]

repository = ContactRepository("data/automated-wishes.db")
repository.save_contacts(contacts, source="carddav")

stored_contacts = repository.get_contacts()

print(f"Stored {len(stored_contacts)} contacts")

for contact in stored_contacts[:10]:
    print(dict(contact))