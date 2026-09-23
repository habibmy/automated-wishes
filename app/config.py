import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    carddav_url: str
    carddav_username: str
    carddav_password: str
    carddav_timeout: int
    wishes_include_group: str
    wishes_exclude_group: str
    timezone: str
    dry_run: bool
    reminder_days_before: int
    ntfy_topic_url: str
    reminder_check_time: str


def load_settings() -> Settings:
    return Settings(
        carddav_url=os.environ["CARDDAV_URL"],
        carddav_username=os.environ["CARDDAV_USERNAME"],
        carddav_password=os.environ["CARDDAV_PASSWORD"],
        carddav_timeout=int(
            os.environ.get("CARDDAV_TIMEOUT", "15")
        ),
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
        reminder_days_before=int(
            os.environ.get("REMINDER_DAYS_BEFORE", "10")
        ),
        ntfy_topic_url=os.environ["NTFY_TOPIC_URL"],
        reminder_check_time=os.environ.get(
            "REMINDER_CHECK_TIME",
            "09:00",
        ),
    )