import sqlite3
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
                    UNIQUE(source, source_uid)
                );

                CREATE TABLE IF NOT EXISTS selected_contacts (
                    contact_id INTEGER PRIMARY KEY,
                    FOREIGN KEY(contact_id) REFERENCES contacts(id)
                );
                """
            )

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
                        emails
                    )
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(source, source_uid)
                    DO UPDATE SET
                        name = excluded.name,
                        phones = excluded.phones,
                        emails = excluded.emails
                    """,
                    (
                        source,
                        contact.uid,
                        contact.name,
                        "\n".join(contact.phones),
                        "\n".join(contact.emails),
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
                    emails
                FROM contacts
                ORDER BY name COLLATE NOCASE
                """
            ).fetchall()