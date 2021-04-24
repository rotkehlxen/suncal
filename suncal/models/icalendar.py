import datetime as dt
from suncal.models.googlecal import GoogleCalEvent
from pydantic import BaseModel
from __future__ import annotations


class Vevent(BaseModel):
    dtend: dt.datetime
    dtstart: dt.datetime
    dtstamp: dt.datetime

    @staticmethod
    def fromGoogleCalEvent(e: GoogleCalEvent) -> Vevent:
        ical_event = Vevent(
            dtstart=e.start.dateTime,
            dtend=e.end.dateTime,
            dtstamp=dt.datetime.now(),
        )
        return ical_event


    # vev = Vevent.fromGoogleCalEvent(ge)

class Vcalendar(BaseModel):
    pass
