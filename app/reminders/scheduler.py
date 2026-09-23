import time
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.config import Settings
from app.database.repository import ContactRepository
from app.notifications.ntfy import NtfyNotifier
from app.reminders.service import send_reminders

logger = logging.getLogger(__name__)


def run_scheduler(
    settings: Settings,
    repository: ContactRepository,
    notifier: NtfyNotifier,
) -> None:
    timezone = ZoneInfo(settings.timezone)

    logger.info(
        "Reminder scheduler started (%s)",
        settings.timezone,
    )

    while True:
        now = datetime.now(timezone)
        today = now.date()

        check_time = datetime.strptime(
            settings.reminder_check_time,
            "%H:%M",
        ).time()

        next_run = datetime.combine(
            today,
            check_time,
            tzinfo=timezone,
        )

        if next_run <= now:
            next_run += timedelta(days=1)

        logger.info(
            "Next reminder check: %s",
            next_run.isoformat(),
        )

        seconds_until_next_run = (next_run - now).total_seconds()

        time.sleep(max(1, seconds_until_next_run))

        today = datetime.now(timezone).date()

        sent_count = send_reminders(
            repository=repository,
            notifier=notifier,
            contacts=repository.get_selected_contacts(),
            today=today,
            days_before=settings.reminder_days_before,
        )

        logger.info(
            "Reminder check completed: %d reminder(s) sent",
            sent_count,
        )
