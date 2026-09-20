import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    carddav_url: str
    carddav_username: str
    carddav_password: str
    wishes_include_group: str
    wishes_exclude_group: str
    timezone: str
    dry_run: bool


def load_settings() -> Settings:
    return Settings(
        carddav_url=os.environ["CARDDAV_URL"],
        carddav_username=os.environ["CARDDAV_USERNAME"],
        carddav_password=os.environ["CARDDAV_PASSWORD"],
        wishes_include_group=os.environ.get(
            "WISHES_INCLUDE_GROUP",
            "Wishes",
        ),
        wishes_exclude_group=os.environ.get(
            "WISHES_EXCLUDE_GROUP",
            "No Wishes",
        ),
        timezone=os.environ.get(
            "TIMEZONE",
            "Asia/Kolkata",
        ),
        dry_run=os.environ.get(
            "DRY_RUN",
            "true",
        ).lower() == "true",
    )