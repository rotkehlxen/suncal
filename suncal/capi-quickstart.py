from googleapiclient.discovery import build

from suncal.auth import get_credentials

# read and write access to google calendars AND calendar events:
# TODO: this scope is a bit too extensive - check how to be more specific
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

creds = get_credentials(SCOPES)

print("build service")
service = build("calendar", "v3", credentials=creds)


# it is ok for the event dict to contain None values!!
# it is NOT ok for this dict to contain datetime objects
event = {
    "start": {"date": None, "dateTime": "2021-02-28T16:30:00+01:00", "timeZone": None},
    "end": {"date": None, "dateTime": "2021-03-01T16:30:00+01:00", "timeZone": None},
    "summary": "fake event",
}

event = service.events().insert(calendarId="primary", body=event).execute()
print("Event created: %s" % (event.get("htmlLink")))
service.close()
