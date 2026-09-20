from app.carddav import CardDAVClient
from app.config import load_settings
from app.contacts.parser import parse_contact

settings = load_settings()

client = CardDAVClient(
    settings.carddav_url,
    settings.carddav_username,
    settings.carddav_password,
)

resources = client.fetch_contacts()
contacts = [parse_contact(resource) for resource in resources]

print(f"Imported {len(contacts)} contacts")