from typing import Any, List

from suncal.models.googlecal import GoogleCalEvent

# TODO: turn the following parameters into command line *options*
calendar_id = "sun"
from_t = "2021-05-01"
to_t = "2021=05-02"
event = "sunrise"  # sunrise/sunset/goldenhour
timezone = "Europe/Berlin"
longitude = 13.23
latitude = 52.32
return_val = "api"  # api/ics


def create_calendar_events(
    event: str, from_t: str, to_t: str, timezone: str, longitude: float, latitude: float
) -> List[GoogleCalEvent]:
    pass


def create_calendar_if_not_exists(calendar_id: str, creds: Any) -> None:
    # TODO: correct type annotation of credentials
    pass


def get_credentials():
    # TODO: what is the type of these credentials? add annotation!
    pass


def export_events_to_calendar(calendar_id: str, events: List[GoogleCalEvent]) -> None:
    pass


# main
def suncal(
    calendar_id: str,
    from_t: str,
    to_t: str,
    event: str,
    timezone: str,
    longitude: float,
    latitude: float,
    return_val: str,
) -> None:

    events: List[GoogleCalEvent] = create_calendar_events(
        event, from_t, to_t, timezone, longitude, latitude
    )

    if return_val == "api":

        # get credentials, create them if they do not exist/need to be refreshed (authentication flow)
        creds = get_credentials()

        # check if calendar with provided id exists, if not create it
        # (make sure the calendar exists, if not, stop right here)
        create_calendar_if_not_exists(calendar_id, creds)

        export_events_to_calendar(calendar_id, events)

    else:
        # export events to ics file with specified path
        pass
