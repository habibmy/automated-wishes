from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import load_settings
from app.database.repository import ContactRepository
from app.notifications.ntfy import NtfyNotifier
from app.reminders.service import send_reminders


def run_reminder_check() -> int:
    settings = load_settings()
    repository = ContactRepository("data/automated-wishes.db")
    notifier = NtfyNotifier(settings.ntfy_topic_url)

    timezone = ZoneInfo(settings.timezone)
    today = datetime.now(timezone).date()

    sent_count = send_reminders(
        repository=repository,
        notifier=notifier,
        contacts=repository.get_selected_contacts(),
        today=today,
        days_before=settings.reminder_days_before,
    )

    return sent_count


if __name__ == "__main__":
    count = run_reminder_check()
    print(f"Sent {count} reminder(s).")