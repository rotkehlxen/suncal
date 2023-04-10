import datetime as dt
from typing import List
from typing import Optional
from timezonefinder import TimezoneFinder

import click

from suncal.auth import get_credentials
from suncal.cli import common_suncal_options
from suncal.fileio import export_events_to_ics
from suncal.models.astro import CALC
from suncal.models.astro import Location
from suncal.models.googlecal import GoogleCalEvent
from suncal.models.googlecal import export_events_to_google_calendar
from suncal.models.googlecal import get_sun_calendar_id
from suncal.utils import collect_cli_arguments
from suncal.utils import date_range

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]


def create_calendar_events(
    event: str, from_date: dt.date, to_date: dt.date, location: Location
) -> List[GoogleCalEvent]:
    """
    Calculate event times for any of the events of type suncal.models.astro.Event between [from_date] and [to_date].
    If the events exist, export them to a GoogleCalEvent and append them to the list of calendar events.
    """

    calendar_events: List = []
    dates = date_range(from_date, to_date)

    for date in dates:
        celestial_event = CALC[event](date, location)
        if celestial_event:
            calendar_events.append(
                GoogleCalEvent.from_celestial_event(celestial_event)
            )

    return calendar_events


def suncal_main(
    from_date: dt.date,
    to_date: dt.date,
    event_name: str,
    longitude: float,
    latitude: float,
    return_val: str,
    timezone: Optional[str] = None,
    filename: Optional[str] = None,
    calendar_title: Optional[str] = None,
) -> None:

    assert to_date >= from_date, "to_date must be >= from_date."

    tf = TimezoneFinder()
    timezone = timezone or tf.timezone_at(lng=longitude, lat=latitude)
    location = Location(
        timezone=timezone, longitude=longitude, latitude=latitude
    )

    events: List[GoogleCalEvent] = create_calendar_events(
        event_name, from_date, to_date, location
    )

    if events:

        if return_val == "api":
            assert calendar_title is not None

            # refresh access tokens or create them if they do not exist (authentication flow)
            credentials = get_credentials(SCOPES)

            # check if calendar with provided title exists, if not create it and always return the id of the calendar
            google_calendar_id = get_sun_calendar_id(
                calendar_title, timezone, credentials
            )

            export_events_to_google_calendar(
                google_calendar_id, events, credentials
            )

        else:
            # export events to ics file with specified name
            export_events_to_ics(events, event_name, filename)

    else:
        click.echo(
            f"*** {event_name.title()} could not be calculated for the specified location. "
            f"No calendar events created. ***"
        )


# root command "suncal"  -----------------------------------------------------------------------------------------------
@click.group()
def suncal():
    pass


# sub-command "api" ----------------------------------------------------------------------------------------------------
@suncal.command()
@common_suncal_options
@click.option(
    "--cal",
    "calendar_title",
    type=click.STRING,
    required=True,
    help="Google calendar name.",
)
def api(
    dev_mode: bool,
    calendar_title: str,
    from_date: dt.date,
    to_date: dt.date,
    event_name: str,
    timezone: str,
    longitude: float,
    latitude: float,
) -> None:
    """Calculate suncal.models.astro.Event for provided range of dates and export calendar events directly
    to Google Calendar.
    """
    if not dev_mode:
        suncal_main(
            calendar_title=calendar_title,
            from_date=from_date,
            to_date=to_date,
            event_name=event_name,
            timezone=timezone,
            longitude=longitude,
            latitude=latitude,
            return_val="api",
        )
    else:
        # print all parsed arguments to the console (as dict)
        collect_cli_arguments(
            dev_mode=dev_mode,
            calendar_title=calendar_title,
            from_date=from_date,
            to_date=to_date,
            event=event_name,
            timezone=timezone,
            longitude=longitude,
            latitude=latitude,
        )


# sub-command "ics" ----------------------------------------------------------------------------------------------------
@suncal.command()
@common_suncal_options
@click.option(
    "--filename",
    type=click.STRING,
    required=False,
    help="Name of ics file. Optional.",
)
def ics(
    dev_mode: bool,
    from_date: dt.date,
    to_date: dt.date,
    event_name: str,
    longitude: float,
    latitude: float,
    timezone: str,
    filename: Optional[str] = None,
) -> None:
    """
    Calculate suncal.models.astro.Event for provided range of dates and export them to ics file.
    """
    if not dev_mode:
        suncal_main(
            from_date=from_date,
            to_date=to_date,
            event_name=event_name,
            longitude=longitude,
            latitude=latitude,
            return_val="ics",
            filename=filename,
            timezone=timezone,
        )
    else:
        # print all parsed arguments to the console (as dict)
        collect_cli_arguments(
            dev_mode=dev_mode,
            from_date=from_date,
            to_date=to_date,
            event=event_name,
            longitude=longitude,
            latitude=latitude,
            filename=filename,
            timezone=timezone,
        )
