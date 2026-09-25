import os
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml
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


def _get_positive_int(value, name: str) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be an integer") from error

    if result <= 0:
        raise ValueError(f"{name} must be greater than 0")

    return result


def _get_non_negative_int(value, name: str) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be an integer") from error

    if result < 0:
        raise ValueError(f"{name} must not be negative")

    return result


def _get_check_time(value: str) -> str:
    try:
        datetime.strptime(value, "%H:%M")
    except (TypeError, ValueError) as error:
        raise ValueError("reminder check time must use HH:MM format") from error

    return value


def _get_timezone(value: str) -> str:
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as error:
        raise ValueError(f"Invalid timezone: {value}") from error

    return value


def load_settings() -> Settings:
    with open("config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    carddav = config.get("carddav", {})
    reminders = config.get("reminders", {})
    notifications = config.get("notifications", {})

    carddav_timeout = os.environ.get(
        "CARDDAV_TIMEOUT",
        carddav.get("timeout", 15),
    )

    reminder_days_before = os.environ.get(
        "REMINDER_DAYS_BEFORE",
        reminders.get("days_before", 10),
    )

    reminder_check_time = os.environ.get(
        "REMINDER_CHECK_TIME",
        reminders.get("check_time", "09:00"),
    )

    timezone = os.environ.get(
        "TIMEZONE",
        reminders.get("timezone", "Asia/Kolkata"),
    )

    return Settings(
        carddav_url=os.environ["CARDDAV_URL"],
        carddav_username=os.environ["CARDDAV_USERNAME"],
        carddav_password=os.environ["CARDDAV_PASSWORD"],
        carddav_timeout=_get_positive_int(
            carddav_timeout,
            "carddav timeout",
        ),
        wishes_include_group=os.environ.get(
            "WISHES_INCLUDE_GROUP",
            carddav.get("include_group", "Wishes"),
        ),
        wishes_exclude_group=os.environ.get(
            "WISHES_EXCLUDE_GROUP",
            carddav.get("exclude_group", "No Wishes"),
        ),
        timezone=_get_timezone(timezone),
        dry_run=os.environ.get(
            "DRY_RUN",
            str(notifications.get("dry_run", True)),
        ).lower()
        == "true",
        reminder_days_before=_get_non_negative_int(
            reminder_days_before,
            "reminder days before",
        ),
        ntfy_topic_url=os.environ["NTFY_TOPIC_URL"],
        reminder_check_time=_get_check_time(reminder_check_time),
    )
