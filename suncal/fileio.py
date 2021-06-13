import datetime as dt
from typing import List, Optional

from suncal.models.icalendar import create_ics_content
from suncal.models.googlecal import GoogleCalEvent


def list_to_file(lines: List[str], filename: str) -> None:
    with open(filename, 'a') as f:
        f.writelines([line + '\n' for line in lines])


def ics_filename(
    calendar_title: str, timezone: str, local_time_now: dt.datetime
) -> str:
    # the only "problematic" character in IANA timezone strings is the "/"
    timezone_str = timezone.replace("/", "-")
    return f"{calendar_title.title()}_{timezone_str}_{local_time_now.strftime('%Y%m%d_%H%M%S')}.ics"


def export_events_to_ics(
    events: List[GoogleCalEvent],
    calendar_title: str,
    timezone: str,
    filename: Optional[str],
) -> None:
    filename = filename or ics_filename(
        calendar_title=calendar_title,
        timezone=timezone,
        local_time_now=dt.datetime.now(),
    )
    # check that filename provided by user has .ics ending, if not, add it
    if not filename.endswith('.ics'):
        filename += '.ics'
    # create ics content as list of strings
    ics_content = create_ics_content(calendar_title, timezone, events)
    print(f"Exporting events to {filename} ...")
    # write to file
    list_to_file(ics_content, filename)
    print("... Done.")
