import datetime as dt
from typing import List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from suncal.auth import get_credentials
from suncal.models.astro import Celestial
from suncal.models.googlecal import GoogleCalEvent
from suncal.models.googlecal import GoogleCalTime
from suncal.models.googlecal import get_sun_calendar_id
from suncal.utils import date_range

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]


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
        event_parameters = Celestial(
            timezone=timezone, date=date, longitude=longitude, latitude=latitude
        ).events[event]
        # create calendar event and append to list, only if astral could calculate valid datetimes
        if event_parameters['start'] and event_parameters['end']:
            gcal_event = GoogleCalEvent(
                start=GoogleCalTime(
                    dateTime=event_parameters['start'], timeZone=timezone
                ),
                end=GoogleCalTime(
                    dateTime=event_parameters['end'], timeZone=timezone
                ),
                summary=event_parameters['gcal_summary'],
            )
            calendar_events.append(gcal_event)
        else:
            print(
                f"{event.title()} could not be calculated for {date} at longitude {longitude} and latitude {latitude}."
            )

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


# TODO: turn the following function into command line app using Typer
# TODO: longitude  in [-180, 180], latitude in [-90, 90]. Catch values outside of these intervals during processing
# TODO: of command line parameters and exit

# main
def suncal(
    calendar_title: str,  # name of target calendar
    from_date: dt.date,  # create events from this date ...
    to_date: dt.date,  # ... to this date
    event: str,  # sunrise/sunset/golden-hour-morning/golden-hour-evening
    timezone: str,  # e.g. "Europe/Berlin"
    longitude: float,  # e.g. 13.23
    latitude: float,  # e.g. 52.32
    return_val: str,  # api/ics
) -> None:

    events: List[GoogleCalEvent] = create_calendar_events(
        event, from_date, to_date, timezone, longitude, latitude
    )

    if events:

        if return_val == "api":

            # get credentials, create them if they do not exist/need to be refreshed (authentication flow)
            credentials = get_credentials(SCOPES)

            # check if calendar with provided title exists, if not create it and always return the id of the calendar
            google_calendar_id = get_sun_calendar_id(
                calendar_title, timezone, credentials
            )

            export_events_to_calendar(google_calendar_id, events, credentials)

        else:
            pass

    else:
        print(
            f"*** {event.title()} could not be calculated for the specified location. "
            f"No calendar events created. ***"
        )
