import os
import requests
from dotenv import load_dotenv

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from icalendar import Calendar
import recurring_ical_events


def get_events_on_date(input_date):
    load_dotenv()
    cal_url = os.getenv("CALENDAR_URL")

    if not cal_url:
        raise ValueError("The 'url' environment variable is not set.")

    response = requests.get(url=cal_url, timeout=30)
    response.raise_for_status()

    calendar = Calendar.from_ical(response.content)

    tz = ZoneInfo("America/New_York")
    start = datetime.combine(input_date, datetime.min.time(), tzinfo=tz)
    end = start + timedelta(days=1)

    return recurring_ical_events.of(calendar).between(start, end)


if __name__ == "__main__":
    occurrences = get_events_on_date(date(2026, 4, 8))

    for event in occurrences:
        print()
        print(
            event.get("SUMMARY"),
            event.decoded("DTSTART"),
            event.decoded("DTEND"),
            event.get("RECURRENCE-ID"),
        )