import datetime as dt
from typing import List
from typing import Optional

from suncal.models.googlecal import GoogleCalEvent
from suncal.models.icalendar import create_ics_content


def list_to_file(lines: List[str], filename: str) -> None:
    with open(filename, 'a') as f:
        f.writelines([line + '\n' for line in lines])


def ics_filename(event_name: str, local_time_now: dt.datetime) -> str:
    return (
        f"{event_name.title()}_{local_time_now.strftime('%Y%m%d_%H%M%S')}.ics"
    )


def export_events_to_ics(
    events: List[GoogleCalEvent],
    event_name: str,
    filename: Optional[str],
) -> None:
    filename = filename or ics_filename(
        event_name=event_name,
        local_time_now=dt.datetime.now(),
    )
    # check that filename provided by user has .ics ending, if not, add it
    if not filename.endswith('.ics'):
        filename += '.ics'
    # create ics content as list of strings
    ics_content = create_ics_content(events)
    print(f"Exporting events to {filename} ...")
    # write to file
    list_to_file(ics_content, filename)
    print("... Done.")
