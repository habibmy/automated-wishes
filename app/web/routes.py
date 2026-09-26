from datetime import date

import requests
import yaml
from flask import Blueprint, redirect, render_template, request, url_for

from app.carddav import CardDAVClient, CardDAVError
from app.config import _build_settings, load_settings
from app.database.repository import ContactRepository
from app.notifications.ntfy import NtfyNotifier
from app.reminders.service import upcoming_occasions
from app.sync.carddav import sync_carddav_contacts

contacts_bp = Blueprint("contacts", __name__)

repository = ContactRepository("data/automated-wishes.db")


@contacts_bp.route("/", methods=["GET", "POST"])
def contacts():
    if request.method == "POST":
        contact_ids = {
            int(contact_id) for contact_id in request.form.getlist("contact_ids")
        }
        repository.set_selected_contacts(contact_ids)
        return redirect(url_for("contacts.contacts"))

    contacts = repository.get_contacts()
    selected_contact_ids = repository.get_selected_contact_ids()

    return render_template(
        "contacts.html",
        contacts=contacts,
        selected_contact_ids=selected_contact_ids,
        synced=request.args.get("synced"),
    )


@contacts_bp.route("/sync", methods=["POST"])
def sync():
    settings = load_settings()

    client = CardDAVClient(
        settings.carddav_url,
        settings.carddav_username,
        settings.carddav_password,
    )

    try:
        count = sync_carddav_contacts(
            client,
            repository,
        )
    except CardDAVError as error:
        return render_template(
            "contacts.html",
            contacts=repository.get_contacts(),
            selected_contact_ids=repository.get_selected_contact_ids(),
            sync_error=str(error),
        )

    return redirect(
        url_for(
            "contacts.contacts",
            synced=count,
        )
    )


@contacts_bp.route("/upcoming")
def upcoming():
    selected_contacts = repository.get_selected_contacts()

    occasions = upcoming_occasions(
        selected_contacts,
        today=date.today(),
        within_days=30,
    )

    return render_template(
        "upcoming.html",
        occasions=occasions,
        today=date.today(),
    )


@contacts_bp.route("/history")
def history():
    reminders = repository.get_reminder_history()

    return render_template(
        "history.html",
        reminders=reminders,
    )


@contacts_bp.route("/settings", methods=["GET", "POST"])
def settings():
    settings = load_settings()

    if request.method == "POST":
        try:
            carddav_timeout = int(request.form.get("carddav_timeout", ""))
            reminder_days_before = int(request.form.get("reminder_days_before", ""))
        except ValueError:
            return render_template(
                "settings.html",
                settings=settings,
                error="Timeout and days before must be valid numbers.",
            )

        config = {
            "carddav": {
                "timeout": carddav_timeout,
                "include_group": request.form.get("wishes_include_group", ""),
                "exclude_group": request.form.get("wishes_exclude_group", ""),
            },
            "reminders": {
                "timezone": request.form.get("timezone", ""),
                "days_before": reminder_days_before,
                "check_time": request.form.get("reminder_check_time", ""),
            },
            "notifications": {
                "dry_run": request.form.get("dry_run") == "true",
            },
        }

        try:
            _build_settings(config)
        except (ValueError, TypeError) as exc:
            return render_template(
                "settings.html",
                settings=settings,
                error=str(exc),
            )

        with open("config.yaml", "w", encoding="utf-8") as file:
            yaml.safe_dump(config, file, sort_keys=False)

        return redirect(url_for("contacts.settings", saved=1))

    return render_template(
        "settings.html",
        settings=settings,
        saved=request.args.get("saved"),
    )


@contacts_bp.route("/settings/test-notification", methods=["POST"])
def test_notification():
    settings = load_settings()
    notifier = NtfyNotifier(settings.ntfy_topic_url)

    try:
        notifier.send(
            title="Automated Wishes test",
            message="Test notification sent successfully.",
        )
    except requests.RequestException as exc:
        return render_template(
            "settings.html",
            settings=settings,
            error=f"Failed to send test notification: {exc}",
        )

    return redirect(url_for("contacts.settings", test_sent=1))
