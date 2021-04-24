import datetime as dt
from typing import List
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from suncal.auth import get_credentials
from suncal.date_utils import date_range
from suncal.models.astro import Celestial
from suncal.models.googlecal import GoogleCalEvent
from suncal.models.googlecal import GoogleCalTime
from suncal.models.googlecal import get_sun_calendar_id

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

# TODO: turn the following parameters into command line *options*
calendar_title = (
    "sun"  # for personal use it may be better to use sth like 'sun berlin'
)
from_date = dt.date(2021, 5, 1)  # would be string "2021-05-01" in cli
to_date = dt.date(2021, 5, 2)  # would be string "2021=05-02" in cli
event = "sunrise"  # sunrise/sunset/goldenhour
timezone = "Europe/Berlin"
longitude = 13.23
latitude = 52.32
return_val = "api"  # api/ics


def create_calendar_events(
    event: str,
    from_date: dt.date,
    to_date: dt.date,
    timezone: str,
    longitude: float,
    latitude: float,
) -> List[GoogleCalEvent]:

    calendar_events: List = []
    dates = date_range(from_date, to_date)
    for date in dates:
        # calculate times of sun event for this date and location
        sun_parameters = Celestial(
            timezone=timezone, date=date, longitude=longitude, latitude=latitude
        ).event
        # create calendar event and append to list
        gcal_event = GoogleCalEvent(
            start=GoogleCalTime(
                dateTime=sun_parameters[event]['start'], timeZone=timezone
            ),
            end=GoogleCalTime(
                dateTime=sun_parameters[event]['end'], timeZone=timezone
            ),
            summary=sun_parameters[event]['gcal_summary'],
        )
        calendar_events.append(gcal_event)

    return calendar_events


def export_events_to_calendar(
    google_calendar_id: str,
    events: List[GoogleCalEvent],
    credentials: Credentials,
) -> None:

    print("Creating calendar events ...")
    with build("calendar", "v3", credentials=credentials) as service:
        for google_cal_event in events:
            service.events().insert(
                calendarId=google_calendar_id, body=google_cal_event.payload()
            ).execute()
    print("... DONE.")


def export_events_to_ics(
    events: List[GoogleCalEvent], filename: Optional[str]
) -> None:
    pass


# main
def suncal(
    calendar_title: str,
    from_date: dt.date,
    to_date: dt.date,
    event: str,
    timezone: str,
    longitude: float,
    latitude: float,
    return_val: str,
    filename: Optional[str] = None,  # only needed when return val is "ics"
) -> None:

    events: List[GoogleCalEvent] = create_calendar_events(
        event, from_date, to_date, timezone, longitude, latitude
    )

    if return_val == "api":

        # get credentials, create them if they do not exist/need to be refreshed (authentication flow)
        credentials = get_credentials(SCOPES)

        # check if calendar with provided title exists, if not create it and always return the id of the calendar
        google_calendar_id = get_sun_calendar_id(
            calendar_title, timezone, credentials
        )

        export_events_to_calendar(google_calendar_id, events, credentials)

    else:
        # export events to ics file with specified path
        export_events_to_ics(events, filename)
