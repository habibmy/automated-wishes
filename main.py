from app.carddav import CardDAVClient
from app.config import load_settings


def main():
    settings = load_settings()

    client = CardDAVClient(
        url=settings.carddav_url,
        username=settings.carddav_username,
        password=settings.carddav_password,
    )

    resources = client.fetch_contacts()

    print(f"Retrieved {len(resources)} CardDAV resources")

    for resource in resources[:3]:
        print(f"- {resource.href}")


if __name__ == "__main__":
    main()