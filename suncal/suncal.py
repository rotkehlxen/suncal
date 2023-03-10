import datetime as dt
from typing import List
from typing import Optional

import click

from suncal.auth import get_credentials
from suncal.cli import IANATimeZoneString
from suncal.cli import common_suncal_options
from suncal.fileio import export_events_to_ics
from suncal.models.astro import Celestial
from suncal.models.googlecal import GoogleCalEvent
from suncal.models.googlecal import GoogleCalTime
from suncal.models.googlecal import export_events_to_google_calendar
from suncal.models.googlecal import get_sun_calendar_id
from suncal.utils import collect_cli_arguments
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

        # create an all-day event for moon phase
        if event == 'moonphase':
            if event_parameters['start']:
                gcal_event = GoogleCalEvent(
                    start=GoogleCalTime(
                        date=event_parameters['start'], timezone=timezone
                    ),
                    end=GoogleCalTime(
                        date=event_parameters['end'], timezone=timezone
                    ),
                    summary=event_parameters['gcal_summary'],
                )
                calendar_events.append(gcal_event)
        else:
            if event_parameters['start']:
                gcal_event = GoogleCalEvent(
                    start=GoogleCalTime(dateTime=event_parameters['start']),
                    end=GoogleCalTime(dateTime=event_parameters['end']),
                    summary=event_parameters['gcal_summary'],
                )
                calendar_events.append(gcal_event)
            else:
                print(
                    f"No {event.title()} for {date} at longitude {longitude} and latitude {latitude}."
                )

    return calendar_events


def suncal_main(
    from_date: dt.date,
    to_date: dt.date,
    event_name: str,
    longitude: float,
    latitude: float,
    return_val: str,
    filename: Optional[str] = None,
    calendar_title: Optional[str] = None,
    timezone: Optional[str] = None,
) -> None:

    assert to_date >= from_date, "to_date must be >= from_date."
    timezone = timezone or "UTC"

    events: List[GoogleCalEvent] = create_calendar_events(
        event_name, from_date, to_date, timezone, longitude, latitude
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
@click.option(
    "--timezone",
    type=IANATimeZoneString(),
    help="Default timezone of google calendar. IANA timezone string. Case-insensitive matching enabled.",
    required=True,
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
    """Calculate sunrise/sunset/moonrise/moonset/moonphase for provided range of dates
    and export calendar events directly to google calendar.
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
    filename: Optional[str] = None,
) -> None:
    """Calculate sunrise/sunset/moonrise/moonset/moonphase for provided range of dates
    and export them to ics file.
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
        )
