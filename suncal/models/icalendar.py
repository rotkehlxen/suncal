from __future__ import annotations

import datetime as dt
from uuid import uuid4

from pydantic import BaseModel  # pylint: disable=E0611
from pydantic import field_validator

from suncal.models.googlecal import GoogleCalEvent
from suncal.utils import aware_datetime_to_ical_date_with_utc_time


class VEvent(BaseModel):
    """Object representation of icalendar VEVENT.
    IMPORTANT: all VEvents of an icalendar have to be initialised with the same [dtstamp],
    using e.g. dt.datetime.now(dt.timezone.utc) defined previously."""

    dtend: dt.datetime | dt.date  # start datetime (timezone aware) or date
    dtstart: dt.datetime | dt.date  # end datetime (timezone aware) or date
    dtstamp: dt.datetime  # datetime of ics file creation (timezone aware)
    uid: str  # unique identifier of icalendar event
    summary: str  # event title
    transp: str  # transparency of event

    @field_validator("dtend", "dtstart", "dtstamp", mode='after')
    @classmethod
    def validate_timezone_awareness(
        cls, timestamp: dt.datetime | dt.date
    ) -> dt.datetime | dt.date:
        if isinstance(timestamp, dt.datetime):
            if timestamp.tzinfo is None and timestamp.utcoffset() is None:
                raise ValueError("All datetimes must be timezone-aware!")
        return timestamp

    @staticmethod
    def fromGoogleCalEvent(ge: GoogleCalEvent, dtstamp: dt.datetime) -> VEvent:
        ical_event = VEvent(
            dtstart=ge.start.datetime or ge.start.date,
            dtend=ge.end.datetime or ge.end.date,
            dtstamp=dtstamp,
            uid=f"{uuid4()}@itsalwaysbeen.photography",
            summary=ge.summary,
            transp=ge.transparency,
        )
        return ical_event

    # vev = VEvent.fromGoogleCalEvent(ge, dtstamp)

    def to_ics(self) -> list[str]:
        """Create lines in ics file from VEvent class object."""

        def ics_date_format(date: dt.date) -> str:
            return f";VALUE=DATE:{date.strftime('%Y%m%d')}"

        dtstart_str = (
            ics_date_format(self.dtstart)
            if type(self.dtstart) == dt.date
            else f":{aware_datetime_to_ical_date_with_utc_time(self.dtstart)}"  # type: ignore
        )
        dtend_str = (
            ics_date_format(self.dtend)
            if type(self.dtend) == dt.date
            else f":{aware_datetime_to_ical_date_with_utc_time(self.dtend)}"  # type: ignore
        )

        ics_entry = [
            'BEGIN:VEVENT',
            f'DTSTART{dtstart_str}',
            f'DTEND{dtend_str}',
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
    prodid: str = (
        "//rotkehlxen//suncal//EN"  # identifier of product that created this file
    )

    def header(self) -> list[str]:
        """Create icalender header. Items in returned list correspond to lines in ics file."""
        icalendar_header = [
            'BEGIN:VCALENDAR',
            f'PRODID:-{self.prodid}',
            f'VERSION:{self.version}',
            f'CALSCALE:{self.cascale}',
            f'METHOD:{self.method}',
        ]
        return icalendar_header

    @classmethod
    def footer(cls) -> list[str]:
        """Create icalender footer."""
        return ['END:VCALENDAR']


def create_ics_content(gcal_events: list[GoogleCalEvent]) -> list[str]:
    """Create all lines of ics file as list of strings."""
    dtstamp = dt.datetime.now(dt.timezone.utc)
    vcalendar = VCalendar()

    # header
    ics_content = vcalendar.header()
    # add google calendar events one by one
    for gcal_event in gcal_events:
        vevent = VEvent.fromGoogleCalEvent(ge=gcal_event, dtstamp=dtstamp)
        ics_content += vevent.to_ics()
    # end with footer
    ics_content += vcalendar.footer()

    return ics_content
