from __future__ import annotations

import datetime as dt
from typing import List

from pydantic import BaseModel  # pylint: disable=E0611
from pydantic import validator

from suncal.models.googlecal import GoogleCalEvent


class VEvent(BaseModel):
    dtend: dt.datetime  # start datetime (timezone aware)
    dtstart: dt.datetime  # end datetime (timezone aware)
    dtstamp: dt.datetime  # datetime of ics file creation (timezone aware)
    uid: str  # unique identifier of icalendar event
    summary: str  # event title
    transp: str  # transparency of event

    @validator("dtend", "dtstart", "dtstamp")
    def validate_timezone_awareness(cls, date_time):  # pylint: disable=E0213
        assert (
            date_time.tzinfo is not None and date_time.utcoffset() is not None
        ), "All datetimes must be timezone-aware!"

    @staticmethod
    def fromGoogleCalEvent(e: GoogleCalEvent) -> VEvent:
        # TODO: these are more or less incorrect placeholders for now:
        ical_event = VEvent(
            dtstart=e.start.dateTime,
            dtend=e.end.dateTime,
            dtstamp=dt.datetime.now(
                dt.timezone.utc
            ),  # TODO: not sure if all events in calendar need same dtstamp
            uid="",
            summary="sth",
            transp=e.transparency,
        )
        return ical_event

    # vev = Vevent.fromGoogleCalEvent(ge)


class VCalendar(BaseModel):
    method: str = (
        "PUBLISH"  # optional, included to mirror google calendar ics export
    )
    cascale: str = (
        "GREGORIAN"  # optional, included to mirror google calendar ics export
    )
    version: str = "2.0"  # icalendar version
    x_wr_calname: str  # name of the calendar, specific to google calendar, ignored by other apps
    x_wr_timezone: str  # e.g. "Europe/Berlin", specific to google calendar, ignored by other apps
    prodid: str = "PLACEHOLDER"  # identifier of product that created this file

    def header(self) -> List[str]:
        """Create icalender header. Items in returned list correspond to lines in ics file. """
        icalendar_header = [
            'BEGIN:VCALENDAR',
            f'PRODID:{self.prodid}' f'VERSION:{self.version}',
            f'CALSCALE:{self.cascale}',
            f'METHOD:{self.method}',
            f'X-WR-CALNAME:{self.x_wr_calname}',
            f'X-WR-TIMEZONE:{self.x_wr_timezone}',
        ]
        return icalendar_header

    @classmethod
    def footer(cls) -> List[str]:
        """ Create icalender footer. """
        return ['END:VCALENDAR']
