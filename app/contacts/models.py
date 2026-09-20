from dataclasses import dataclass


@dataclass(frozen=True)
class Contact:
    uid: str
    name: str
    phones: tuple[str, ...]
    emails: tuple[str, ...]