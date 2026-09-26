import sqlite3
from datetime import date, datetime
from pathlib import Path

from app.contacts.models import Contact


class ContactRepository:
    def __init__(self, database_path: str):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    source_uid TEXT NOT NULL,
                    name TEXT NOT NULL,
                    phones TEXT NOT NULL,
                    emails TEXT NOT NULL,
                    birthday TEXT,
                    anniversary TEXT,
                    UNIQUE(source, source_uid)
                );

                CREATE TABLE IF NOT EXISTS selected_contacts (
                    contact_id INTEGER PRIMARY KEY,
                    FOREIGN KEY(contact_id) REFERENCES contacts(id)
                );

                CREATE TABLE IF NOT EXISTS sent_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_uid TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    occasion_date TEXT NOT NULL,
                    sent_at TEXT NOT NULL,
                    UNIQUE(contact_uid, kind, occasion_date)
                );

                """
            )

            columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(contacts)").fetchall()
            }

            if "birthday" not in columns:
                connection.execute("ALTER TABLE contacts ADD COLUMN birthday TEXT")

            if "anniversary" not in columns:
                connection.execute("ALTER TABLE contacts ADD COLUMN anniversary TEXT")

    def save_contacts(
        self,
        contacts: list[Contact],
        source: str,
    ) -> None:
        with self._connect() as connection:
            for contact in contacts:
                connection.execute(
                    """
                    INSERT INTO contacts (
                        source,
                        source_uid,
                        name,
                        phones,
                        emails,
                        birthday,
                        anniversary
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(source, source_uid)
                    DO UPDATE SET
                        name = excluded.name,
                        phones = excluded.phones,
                        emails = excluded.emails,
                        birthday = excluded.birthday,
                        anniversary = excluded.anniversary
                    """,
                    (
                        source,
                        contact.uid,
                        contact.name,
                        "\n".join(contact.phones),
                        "\n".join(contact.emails),
                        contact.birthday.isoformat() if contact.birthday else None,
                        contact.anniversary.isoformat()
                        if contact.anniversary
                        else None,
                    ),
                )

    def get_contacts(self) -> list[sqlite3.Row]:
        with self._connect() as connection:
            return connection.execute(
                """
                SELECT
                    id,
                    source,
                    source_uid,
                    name,
                    phones,
                    emails,
                    birthday,
                    anniversary
                FROM contacts
                ORDER BY name COLLATE NOCASE
                """
            ).fetchall()

    def get_selected_contact_ids(self) -> set[int]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT contact_id FROM selected_contacts"
            ).fetchall()

        return {row["contact_id"] for row in rows}

    def set_selected_contacts(self, contact_ids: set[int]) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM selected_contacts")

            connection.executemany(
                "INSERT INTO selected_contacts (contact_id) VALUES (?)",
                [(contact_id,) for contact_id in contact_ids],
            )

    def get_selected_contacts(self) -> list[Contact]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    source,
                    source_uid,
                    name,
                    phones,
                    emails,
                    birthday,
                    anniversary
                FROM contacts
                WHERE id IN (
                    SELECT contact_id
                    FROM selected_contacts
                )
                ORDER BY name COLLATE NOCASE
                """
            ).fetchall()

        return [self._row_to_contact(row) for row in rows]

    def _row_to_contact(self, row: sqlite3.Row) -> Contact:
        return Contact(
            uid=row["source_uid"],
            name=row["name"],
            phones=tuple(phone for phone in row["phones"].splitlines() if phone),
            emails=tuple(email for email in row["emails"].splitlines() if email),
            birthday=(date.fromisoformat(row["birthday"]) if row["birthday"] else None),
            anniversary=(
                date.fromisoformat(row["anniversary"]) if row["anniversary"] else None
            ),
        )

    def has_sent_reminder(
        self,
        contact_uid: str,
        kind: str,
        occasion_date: date,
    ) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM sent_reminders
                WHERE contact_uid = ?
                AND kind = ?
                AND occasion_date = ?
                LIMIT 1
                """,
                (
                    contact_uid,
                    kind,
                    occasion_date.isoformat(),
                ),
            ).fetchone()

        return row is not None

    def mark_reminder_sent(
        self,
        contact_uid: str,
        kind: str,
        occasion_date: date,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO sent_reminders (
                    contact_uid,
                    kind,
                    occasion_date,
                    sent_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    contact_uid,
                    kind,
                    occasion_date.isoformat(),
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )

    def get_reminder_history(
        self,
        limit: int = 100,
    ) -> list[sqlite3.Row]:
        with self._connect() as connection:
            return connection.execute(
                """
                SELECT
                    sent_reminders.id,
                    sent_reminders.contact_uid,
                    contacts.name,
                    sent_reminders.kind,
                    sent_reminders.occasion_date,
                    sent_reminders.sent_at
                FROM sent_reminders
                LEFT JOIN contacts
                    ON contacts.source_uid = sent_reminders.contact_uid
                ORDER BY sent_reminders.sent_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
