from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Contact:
    uid: str
    name: str
    phones: tuple[str, ...]
    emails: tuple[str, ...]
    birthday: date | None
    anniversary: date | None