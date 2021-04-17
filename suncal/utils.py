import datetime as dt
from typing import List

import pytz


def date_range(date_from: dt.date, date_to: dt.date) -> List[dt.date]:
    """
    Create list of dates from [date_from] to [date_to] including the
    from and to dates.
    """
    return [
        date_from + dt.timedelta(days=i) for i in range((date_to - date_from).days + 1)
    ]


def create_timezone_aware_datetime(
    year: int, month: int, day: int, hour: int, minute: int, second: int, timezone: str
) -> dt.datetime:
    """Create timezone aware datetime object using the IANA timezone string, e.g.  'Europe/Berlin'."""

    naive_datetime = dt.datetime(
        year=year, month=month, day=day, hour=hour, minute=minute, second=second
    )
    timezone_obj = pytz.timezone(timezone)
    aware_datetime = timezone_obj.localize(naive_datetime)
    return aware_datetime
