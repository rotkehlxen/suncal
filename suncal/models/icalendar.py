import datetime as dt
from suncal.models.googlecal import GoogleCalEvent
from pydantic import BaseModel


class Vevent(BaseModel):
    dtend: dt.datetime
    dtstart: dt.datetime
    dtstamp: dt.datetime

    @staticmethod
    def fromGoogleCalEvent(e: GoogleCalEvent) -> Vevent:
        Vevent(
            dtstart=e.start.dateTime,
            dtend=e.end.dateTime,
        )


    # vev = Vevent.fromGoogleCalEvent(ge)

class Vcalendar(BaseModel):
    pass
