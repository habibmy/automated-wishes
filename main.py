from app.config import load_settings


def main():
    settings = load_settings()

    print("Configuration loaded")
    print(f"CardDAV URL: {settings.carddav_url}")
    print(f"CardDAV username: {settings.carddav_username}")
    print(f"Include group: {settings.wishes_include_group}")
    print(f"Exclude group: {settings.wishes_exclude_group}")
    print(f"Timezone: {settings.timezone}")
    print(f"Dry run: {settings.dry_run}")


if __name__ == "__main__":
    main()