from __future__ import annotations

import datetime as dt
from typing import List
from uuid import uuid4

from pydantic import BaseModel  # pylint: disable=E0611
from pydantic import validator

from suncal.date_utils import aware_datetime_to_ical_date_with_utc_time
from suncal.models.googlecal import GoogleCalEvent


class VEvent(BaseModel):
    """Object representation of icalendar VEVENT.
    IMPORTANT: all VEvents of an icalendar have to be initialised with the same [dtstamp],
    using e.g. dt.datetime.now(dt.timezone.utc) defined previously."""

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
        return date_time

    @staticmethod
    def fromGoogleCalEvent(ge: GoogleCalEvent, dtstamp: dt.datetime) -> VEvent:
        ical_event = VEvent(
            dtstart=ge.start.dateTime,
            dtend=ge.end.dateTime,
            dtstamp=dtstamp,
            uid=f"{uuid4()}@itsalwaysbeen.photography",
            summary=ge.summary,
            transp=ge.transparency,
        )
        return ical_event

    # vev = VEvent.fromGoogleCalEvent(ge, dtstamp)

    def to_ics(self) -> List[str]:
        """Create lines in ics file from VEvent class object."""
        ics_entry = [
            'BEGIN:VEVENT',
            f'DTSTART:{aware_datetime_to_ical_date_with_utc_time(self.dtstart)}',
            f'DTEND:{aware_datetime_to_ical_date_with_utc_time(self.dtend)}',
            f'DTSTAMP:{aware_datetime_to_ical_date_with_utc_time(self.dtstamp)}',
            f'UID:{self.uid}',
            f'SUMMARY:{self.summary}',
            f'TRANSP:{self.transp.upper()}',
            'END:VEVENT',
        ]
        return ics_entry


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
    prodid: str = "PLACEHOLDER"  # identifier of product that created this file: TODO: change this!

    def header(self) -> List[str]:
        """Create icalender header. Items in returned list correspond to lines in ics file. """
        icalendar_header = [
            'BEGIN:VCALENDAR',
            f'PRODID:{self.prodid}',
            f'VERSION:{self.version}',
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
