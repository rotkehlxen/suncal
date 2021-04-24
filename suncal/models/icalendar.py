import datetime as dt
class VEvent:
    dtend: dt.datetime
    dtstart: dt.datetime

    @staticmethod
    def fromGoogleCalEvent(e: GoogleCalEvent) -> VEvent:
        VEvent(
            dtstart = e.start.dateTime,
            dtend = e.end.dateTime,
        )
    def someOtherMethod(self):
        pass


    ge: GoogleCalEvent

    vev = VEvent.fromGoogleCalEvent(ge)
    x = vev.someOtherMethod()