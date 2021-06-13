import datetime as dt
from typing import List
from typing import Optional

import click

from suncal.auth import get_credentials
from suncal.cli import IANATimeZoneString
from suncal.date_utils import date_range
from suncal.fileio import export_events_to_ics
from suncal.models.astro import Celestial
from suncal.models.googlecal import GoogleCalEvent
from suncal.models.googlecal import GoogleCalTime
from suncal.models.googlecal import export_events_to_google_calendar
from suncal.models.googlecal import get_sun_calendar_id

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


def suncal_main(
    calendar_title: str,  # name of google target calendar
    from_date: dt.date,  # create events from this date ...
    to_date: dt.date,  # ... to this date
    event: str,  # sunrise/sunset/golden-hour-morning/golden-hour-evening
    timezone: str,  # e.g. "Europe/Berlin"
    longitude: float,  # e.g. 13.23
    latitude: float,  # e.g. 52.32
    return_val: str,  # api/ics
    filename: Optional[str] = None,  # only needed when return val is "ics"
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

            export_events_to_google_calendar(
                google_calendar_id, events, credentials
            )

        else:
            # export events to ics file with specified name
            export_events_to_ics(events, calendar_title, timezone, filename)

    else:
        print(
            f"*** {event.title()} could not be calculated for the specified location. "
            f"No calendar events created. ***"
        )


def collect_cli_arguments(**suncal_kwargs) -> None:
    click.echo(suncal_kwargs)


# cli
@click.command()
@click.option(
    "--cal", "calendar_title", type=click.STRING, help="google calendar name"
)
@click.option(
    "--from",
    "from_date",
    type=click.DateTime(),
    help="First date for which to create events.",
)
@click.option(
    "--to",
    "to_date",
    type=click.DateTime(),
    help="Last date for which to create events.",
)
@click.option(
    "--event",
    type=click.Choice(
        ['sunrise', 'sunset', 'golden-hour-morning', 'golden-hour-evening'],
        case_sensitive=False,
    ),
    help="Calculate start and end time of the selected event.",
)
@click.option(
    "--timezone",
    type=IANATimeZoneString(),
    help="IANA timezone string. Case-insensitive matching enabled.",
)
@click.option(
    "--long",
    "longitude",
    type=click.FloatRange(min=-180.0, max=180.0),
    help="Longitude as float.",
)
@click.option(
    "--lat",
    "latitude",
    type=click.FloatRange(min=-90.0, max=90.0),
    help="Latitude as float.",
)
@click.option(
    "--return-val",
    type=click.Choice(['api', 'ics'], case_sensitive=False),
    help="Write events to google calendar using 'api', write to ics file using 'ics'.",
)
@click.option(
    "--filename",
    type=click.STRING,
    required=False,
    help="Name of ics file. Optional.",
)
@click.option('--dev/--no-dev', 'dev_mode', default=False)
def suncal(
    dev_mode: bool,  # dev mode
    calendar_title: str,  # name of google target calendar
    from_date: dt.date,  # create events from this date ...
    to_date: dt.date,  # ... to this date
    event: str,  # sunrise/sunset/golden-hour-morning/golden-hour-evening
    timezone: str,  # e.g. "Europe/Berlin"
    longitude: float,  # e.g. 13.23
    latitude: float,  # e.g. 52.32
    return_val: str,  # api/ics
    filename: Optional[str] = None,  # only needed when return val is "ics"
) -> None:
    """Calculate sunrise/sunset/golden-hour-morning/golden-hour-evening for provided range of dates
    and export calendar events directly to google calendar or export them to ics file.
    """
    if not dev_mode:
        suncal_main(
            calendar_title,
            from_date,
            to_date,
            event,
            timezone,
            longitude,
            latitude,
            return_val,
            filename,
        )
    else:
        # print all parsed arguments to the console (as dict)
        print("I am in the dev section")
        collect_cli_arguments(
            dev_mode=dev_mode,
            calendar_title=calendar_title,
            from_date=from_date,
            to_date=to_date,
            event=event,
            timezone=timezone,
            longitude=longitude,
            latitude=latitude,
            return_val=return_val,
            filename=filename,
        )
