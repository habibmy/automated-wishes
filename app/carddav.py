from dataclasses import dataclass
from xml.etree import ElementTree

import requests


DAV_NAMESPACE = "DAV:"
CARDDAV_NAMESPACE = "urn:ietf:params:xml:ns:carddav"


@dataclass(frozen=True)
class CardDAVResource:
    href: str
    etag: str | None
    vcard: str


class CardDAVError(Exception):
    """Raised when a CardDAV operation fails."""


class CardDAVClient:
    def __init__(
        self,
        url: str,
        username: str,
        password: str,
    ):
        self.url = url
        self.session = requests.Session()
        self.session.auth = (username, password)

    def fetch_contacts(self) -> list[CardDAVResource]:
        try:
            response = self.session.request(
                method="REPORT",
                url=self.url,
                headers={
                    "Depth": "1",
                    "Content-Type": "application/xml; charset=utf-8",
                },
                data=self._addressbook_query(),
            )
        except requests.RequestException as error:
            raise CardDAVError(f"CardDAV request failed: {error}") from error

        if not response.ok:
            raise CardDAVError(
                f"CardDAV request failed: HTTP {response.status_code} {response.reason}"
            )

        return self._parse_report(response.content)

    @staticmethod
    def _addressbook_query() -> str:
        return """\
<?xml version="1.0" encoding="UTF-8"?>
<card:addressbook-query
    xmlns:d="DAV:"
    xmlns:card="urn:ietf:params:xml:ns:carddav">
    <d:prop>
        <d:getetag />
        <card:address-data />
    </d:prop>
</card:addressbook-query>
"""

    @staticmethod
    def _parse_report(data: bytes) -> list[CardDAVResource]:
        root = ElementTree.fromstring(data)

        resources = []

        for response in root.findall(f"{{{DAV_NAMESPACE}}}response"):
            href_element = response.find(f"{{{DAV_NAMESPACE}}}href")
            address_data = response.find(f".//{{{CARDDAV_NAMESPACE}}}address-data")
            etag_element = response.find(f".//{{{DAV_NAMESPACE}}}getetag")

            if href_element is None or address_data is None:
                continue

            resources.append(
                CardDAVResource(
                    href=href_element.text or "",
                    etag=(etag_element.text if etag_element is not None else None),
                    vcard=address_data.text or "",
                )
            )

        return resources
