from typing import List
from typing import Optional

from google.oauth2.credentials import Credentials

from suncal.auth import get_credentials
from suncal.models.googlecal import create_calendar_if_not_exists
from suncal.utils import date_range
from suncal.models.astro import Celestial
from suncal.models.googlecal import GoogleCalEvent, GoogleCalTime, google_cal_summary

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

# TODO: turn the following parameters into command line *options*
calendar_id = (
    "sun"  # for personal use it may be better to use sth like 'sun berlin'
)
from_date = "2021-05-01"
to_date = "2021=05-02"
event = "sunrise"  # sunrise/sunset/goldenhour
timezone = "Europe/Berlin"
longitude = 13.23
latitude = 52.32
return_val = "api"  # api/ics


def create_calendar_events(
    event: str,
    from_date: str,
    to_date: str,
    timezone: str,
    longitude: float,
    latitude: float,
) -> List[GoogleCalEvent]:

    calendar_events: List = []
    dates = date_range(from_date, to_date)
    for date in dates:
        # calculate times of sun event for this date and location
        sun_event = Celestial(timezone=timezone, date=date, longitude=longitude, latitude=latitude).event()
        # get calendar event summary
        summary = google_cal_summary(event, sun_event['start'])
        # create calendar event and append payload to list
        gcal_event = GoogleCalEvent(start=GoogleCalTime(dateTime=sun_event['start']),
                                    end=GoogleCalTime(dateTime=sun_event['end']),
                                    summary=summary)
        calendar_events.append(gcal_event)

    return calendar_events


def export_events_to_calendar(
    calendar_id: str, events: List[GoogleCalEvent], creds: Credentials
) -> None:
    pass


# main
def suncal(
    calendar_id: str,
    from_date: str,
    to_date: str,
    event: str,
    timezone: str,
    longitude: float,
    latitude: float,
    return_val: str,
) -> None:

    events: List[GoogleCalEvent] = create_calendar_events(
        event, from_date, to_date, timezone, longitude, latitude
    )

    if return_val == "api":

        # get credentials, create them if they do not exist/need to be refreshed (authentication flow)
        creds = get_credentials(SCOPES)

        # check if calendar with provided id exists, if not create it
        # (make sure the calendar exists, if not, stop right here)
        gcal_id: Optional[str] = create_calendar_if_not_exists(
            calendar_id, timezone, creds
        )

        export_events_to_calendar(calendar_id, events, creds)

    else:
        # export events to ics file with specified path
        pass
