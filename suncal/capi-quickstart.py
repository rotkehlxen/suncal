from typing import List

from googleapiclient.discovery import build

from suncal.auth import get_credentials

# read and write access to google calendars AND calendar events:
# TODO: this scope is a bit too extensive - check how to be more specific
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

creds = get_credentials(SCOPES)

# Create calendar event ------------------------------------------------------------------------------------------------
# with build("calendar", "v3", credentials=creds) as service:
#     event = {
#         "start": {
#             "date": None,
#             "dateTime": "2021-02-28T16:30:00+01:00",
#             "timeZone": None,
#         },
#         "end": {
#             "date": None,
#             "dateTime": "2021-03-01T16:30:00+01:00",
#             "timeZone": None,
#         },
#         "summary": "fake event",
#     }
#
#     # TODO: how does that work with id "primary"? for my calendar fields 'id' and 'summary' are my gmail address!
#     # TODO: to create events in sun calendar, do I have to use the id field?
#     event = service.events().insert(calendarId="primary", body=event).execute()
#
# print("Event created: %s" % (event.get("htmlLink")))

# Create new calendar (secondary) --------------------------------------------------------------------------------------
with build("calendar", "v3", credentials=creds) as service:
    calendar = {"summary": "exp calendar", "timeZone": "Europe/Berlin"}

    created_calendar = service.calendars().insert(body=calendar).execute()

print(f"New calendar has id: {created_calendar['id']}.")
print(f"New calendar has summary: {created_calendar['summary']}.")

# Get all your calendars -----------------------------------------------------------------------------------------------
# the result can potentially span several pages (i.e. there is a max number of entries per page!)
with build("calendar", "v3", credentials=creds) as service:
    calendars: List = []
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        calendars = calendars + [
            calendar_list_entry["summary"]
            for calendar_list_entry in calendar_list["items"]
        ]
        page_token = calendar_list.get("nextPageToken")
        if not page_token:
            break

print(calendars)
