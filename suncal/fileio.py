import datetime as dt
from typing import List


def list_to_file(lines: List[str], filename: str) -> None:
    with open(filename, 'a') as f:
        f.writelines([line + '\n' for line in lines])


def ics_filename(
    calendar_title: str, timezone: str, local_time_now: dt.datetime
) -> str:
    # the only "problematic" character in IANA timezone strings is the "/"
    timezone_str = timezone.replace("/", "-")
    return f"{calendar_title.title()}_{timezone_str}_{local_time_now.strftime('%Y%m%d_%H%M%S')}.ics"
