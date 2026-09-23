import requests


class NtfyNotifier:
    def __init__(self, topic_url: str):
        self.topic_url = topic_url

    def send(self, title: str, message: str) -> None:
        response = requests.post(
            self.topic_url,
            headers={
                "Title": title,
            },
            data=message.encode("utf-8"),
            timeout=15,
        )

        response.raise_for_status()