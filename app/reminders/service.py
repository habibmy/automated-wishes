from datetime import date

from app.contacts.models import Contact
from app.reminders.occasions import Occasion, get_upcoming_occasions
from app.database.repository import ContactRepository
from app.notifications.ntfy import NtfyNotifier

def upcoming_occasions(
    contacts: list[Contact],
    today: date,
    within_days: int | None = None,
) -> list[Occasion]:
    occasions: list[Occasion] = []

    for contact in contacts:
        occasions.extend(
            get_upcoming_occasions(contact, today)
        )

    occasions.sort(
        key=lambda occasion: (
            occasion.days_until(today),
            occasion.contact_name.lower(),
        )
    )

    if within_days is not None:
        occasions = [
            occasion
            for occasion in occasions
            if occasion.days_until(today) <= within_days
        ]

    return occasions

def reminder_candidates(
    contacts: list[Contact],
    today: date,
    days_before: int,
) -> list[Occasion]:
    occasions = upcoming_occasions(
        contacts,
        today,
        within_days=days_before,
    )

    return [
        occasion
        for occasion in occasions
        if occasion.days_until(today) == days_before
    ]

def send_reminders(
    repository: ContactRepository,
    notifier: NtfyNotifier,
    contacts: list[Contact],
    today: date,
    days_before: int,
) -> int:
    candidates = reminder_candidates(
        contacts,
        today,
        days_before,
    )

    sent_count = 0

    for occasion in candidates:
        if repository.has_sent_reminder(
            occasion.contact_uid,
            occasion.kind,
            occasion.next_date,
        ):
            continue

        title = (
            "Birthday Reminder"
            if occasion.kind == "birthday"
            else "Anniversary Reminder"
        )

        message = (
            f"{occasion.contact_name}'s "
            f"{occasion.kind} is in {days_before} days "
            f"({occasion.next_date.strftime('%d %B %Y')})."
        )

        notifier.send(title, message)

        repository.mark_reminder_sent(
            occasion.contact_uid,
            occasion.kind,
            occasion.next_date,
        )

        sent_count += 1

    return sent_count