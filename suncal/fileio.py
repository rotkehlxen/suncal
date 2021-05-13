import datetime as dt
from typing import List


def list_to_file(lines: List[str], filename: str) -> None:
    with open(filename, 'a') as f:
        f.writelines([line + '\n' for line in lines])


def ics_filename(
    calendar_title: str, timezone: str, local_time_now: dt.datetime
) -> str:

    # TODO: are there IANA timezones without / in them?
    assert "/" in timezone, "Invalid timezone provided!"
    timezone_splitted = timezone.split("/")
    region = timezone_splitted[0]
    city = timezone_splitted[1]
    return f"{calendar_title.title()}_{region}-{city}_{local_time_now.strftime('%Y%m%d_%H%M%S')}.ics"
