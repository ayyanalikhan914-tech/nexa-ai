import json
import time
from datetime import datetime
from pathlib import Path
from winotify import Notification

REMINDER_FILE = Path(__file__).parent / "reminders.json"


def load_reminders():
    if not REMINDER_FILE.exists():
        return []

    try:
        with open(REMINDER_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return []


def save_reminders(reminders):
    with open(REMINDER_FILE, "w", encoding="utf-8") as file:
        json.dump(reminders, file, indent=4)


def send_notification(message):
    toast = Notification(
        app_id="Nexa AI",
        title="🚀 Nexa AI Reminder",
        msg=message,
        duration="long"
    )

    toast.show()


print("🔔 Nexa Reminder Service Started")


while True:

    reminders = load_reminders()

    current_time = datetime.now()

    changed = False

    for reminder in reminders:

        if reminder.get("done", False):
            continue

        try:
            reminder_time = datetime.fromisoformat(
                reminder["datetime"]
            )
        except Exception:
            continue

        if current_time >= reminder_time:

            send_notification(
                f"🔔 {reminder['text']}"
            )

            reminder["done"] = True
            changed = True

    if changed:
        save_reminders(reminders)

    time.sleep(10)