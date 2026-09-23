from datetime import date

from flask import Blueprint, redirect, render_template, request, url_for

from app.config import load_settings
from app.carddav import CardDAVClient, CardDAVError
from app.database.repository import ContactRepository
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
