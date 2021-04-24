from __future__ import annotations

import datetime as dt

from pydantic import BaseModel  # pylint: disable=E0611
from pydantic import validator

from suncal.models.googlecal import GoogleCalEvent


class Vevent(BaseModel):
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
    def fromGoogleCalEvent(e: GoogleCalEvent) -> Vevent:
        # TODO: these are more or less incorrect placeholders for now:
        ical_event = Vevent(
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


class Vcalendar(BaseModel):
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

    def header(self):
        # header string of icalendar file
        icalendar_header = f""" 
       BEGIN:VCALENDAR\n
       PRODID:{self.prodid}\n
       VERSION:{self.version}\n
       CALSCALE:{self.cascale}\n
       METHOD:{self.method}\n
       X-WR-CALNAME:{self.x_wr_calname}\n
       X-WR-TIMEZONE:{self.x_wr_timezone}
        """
        return icalendar_header

    @classmethod
    def footer(cls):
        # footer string of icalendar file
        return "END:VCALENDAR"
