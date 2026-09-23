import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.config import Settings
from app.database.repository import ContactRepository
from app.notifications.ntfy import NtfyNotifier
from app.reminders.service import send_reminders


def run_scheduler(
    settings: Settings,
    repository: ContactRepository,
    notifier: NtfyNotifier,
) -> None:
    timezone = ZoneInfo(settings.timezone)

    while True:
        now = datetime.now(timezone)
        today = now.date()

        send_reminders(
            repository=repository,
            notifier=notifier,
            contacts=repository.get_selected_contacts(),
            today=today,
            days_before=settings.reminder_days_before,
        )

        tomorrow = today + timedelta(days=1)
        next_run = datetime.combine(
            tomorrow,
            datetime.min.time(),
            tzinfo=timezone,
        )

        seconds_until_next_run = (
            next_run - datetime.now(timezone)
        ).total_seconds()

        time.sleep(max(1, seconds_until_next_run))