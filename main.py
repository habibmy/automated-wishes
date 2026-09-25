import logging
import threading

from app.config import load_settings
from app.database.repository import ContactRepository
from app.notifications.ntfy import NtfyNotifier
from app.reminders.scheduler import run_scheduler
from app.web import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


settings = load_settings()
repository = ContactRepository("data/automated-wishes.db")
notifier = NtfyNotifier(settings.ntfy_topic_url)

scheduler_thread = threading.Thread(
    target=run_scheduler,
    args=(repository, notifier),
    daemon=True,
    name="reminder-scheduler",
)

scheduler_thread.start()

app = create_app()


if __name__ == "__main__":
    app.run(debug=False)
