from __future__ import annotations

import datetime as dt

from pydantic import BaseModel  # pylint: disable=E0611

from suncal.models.googlecal import GoogleCalEvent


class Vevent(BaseModel):
    dtend: dt.datetime
    dtstart: dt.datetime
    dtstamp: dt.datetime
    uid: str
    summary: str
    transp: str

    @staticmethod
    def fromGoogleCalEvent(e: GoogleCalEvent) -> Vevent:
        # TODO: these are more or less incorrect placeholders for now:
        ical_event = Vevent(
            dtstart=e.start.dateTime,
            dtend=e.end.dateTime,
            dtstamp=dt.datetime.now(),
            uid="",
            summary="sth",
            transp=e.transparency,
        )
        return ical_event

    # vev = Vevent.fromGoogleCalEvent(ge)


class Vcalendar(BaseModel):
    pass
