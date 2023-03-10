import datetime as dt
from typing import List

import click
import pytz


def date_range(date_from: dt.date, date_to: dt.date) -> List[dt.date]:
    """
    Create list of dates from [date_from] to [date_to] including the
    from and to dates.
    """
    return [
        date_from + dt.timedelta(days=i)
        for i in range((date_to - date_from).days + 1)
    ]


def tz_aware_dt(
    naive_datetime: dt.datetime,
    timezone: str,
) -> dt.datetime:
    """Create timezone aware datetime object using the IANA timezone string, e.g.  'Europe/Berlin'."""

    assert (
        naive_datetime.tzinfo is None
    ), f"The datetime you provided already is timezone-aware ({naive_datetime.tzinfo})"
    timezone_obj = pytz.timezone(timezone)
    aware_datetime = timezone_obj.localize(naive_datetime)
    return aware_datetime


def aware_datetime_to_ical_date_with_utc_time(
    aware_datetime: dt.datetime,
) -> str:
    """
    Convert time-zone aware datetime to DATE-TIME of icalendar in Form #2. This
    is a quote from the specs in https://tools.ietf.org/html/rfc5545:

    FORM #2: DATE WITH UTC TIME

    The date with UTC time, or absolute time, is identified by a LATIN
    CAPITAL LETTER Z suffix character, the UTC designator, appended to
    the time value.  For example, the following represents January 19,
    1998, at 0700 UTC:

    19980119T070000Z"""

    utc_timezone = pytz.timezone('UTC')
    utc_datetime = aware_datetime.astimezone(utc_timezone)

    return utc_datetime.strftime("%Y%m%dT%H%M%SZ")


def create_batches(list_: List, batch_size: int = 500) -> List[List]:
    """Divide [list_] into batches (sub-lists) of max length [batch_size]."""
    batches = []
    for idx in range(0, len(list_), batch_size):
        batches += [list_[idx : idx + batch_size]]
    return batches


def collect_cli_arguments(**suncal_kwargs) -> None:
    click.echo(suncal_kwargs)
