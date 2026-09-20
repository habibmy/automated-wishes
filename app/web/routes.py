from flask import Blueprint, redirect, render_template, request, url_for

from app.database.repository import ContactRepository

contacts_bp = Blueprint("contacts", __name__)

repository = ContactRepository("data/automated-wishes.db")


@contacts_bp.route("/", methods=["GET", "POST"])
def contacts():
    if request.method == "POST":
        contact_ids = {
            int(contact_id)
            for contact_id in request.form.getlist("contact_ids")
        }

        repository.set_selected_contacts(contact_ids)

        return redirect(url_for("contacts.contacts"))

    contacts = repository.get_contacts()
    selected_contact_ids = repository.get_selected_contact_ids()

    return render_template(
        "contacts.html",
        contacts=contacts,
        selected_contact_ids=selected_contact_ids,
    )