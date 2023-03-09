import datetime as dt

import pytest
from pydantic import ValidationError

from suncal.models.googlecal import GoogleCalEvent
from suncal.models.googlecal import GoogleCalTime
from suncal.models.icalendar import VCalendar
from suncal.models.icalendar import VEvent
from suncal.models.icalendar import create_ics_content
from suncal.utils import create_timezone_aware_datetime

start_datetime = create_timezone_aware_datetime(
    dt.datetime(year=2021, month=2, day=28, hour=16, minute=30, second=0),
    timezone="Europe/Berlin",
)

end_datetime = create_timezone_aware_datetime(
    dt.datetime(year=2021, month=2, day=28, hour=17, minute=30, second=0),
    timezone="Europe/Berlin",
)

start_time = GoogleCalTime(dateTime=start_datetime)
end_time = GoogleCalTime(dateTime=end_datetime)
now = dt.datetime.now(dt.timezone.utc)


def test_vcalendar():
    vcal = VCalendar()

    assert vcal.method == "PUBLISH"
    assert vcal.prodid == "//rotkehlxen//suncal//EN"
    assert vcal.cascale == "GREGORIAN"

    header = vcal.header()
    assert VCalendar.footer() == ["END:VCALENDAR"]
    assert vcal.footer() == ["END:VCALENDAR"]
    assert "METHOD:PUBLISH" in header
    assert header[1] == "PRODID:-//rotkehlxen//suncal//EN"
    assert header[2] == "VERSION:2.0"


def test_vevent():

    # test creation of VEvent from GoogleCalTime

    gcal_event = GoogleCalEvent(
        start=start_time, end=end_time, summary="event_summary"
    )

    vevent = VEvent.fromGoogleCalEvent(ge=gcal_event, dtstamp=now)

    assert vevent.dtend == gcal_event.end.dateTime
    assert vevent.dtstart == gcal_event.start.dateTime
    assert vevent.summary == gcal_event.summary
    assert "itsalwaysbeen.photography" in vevent.uid
    assert vevent.transp == "transparent"
    assert vevent.dtstamp == now

    # test ics format
    ics_export = vevent.to_ics()

    assert isinstance(ics_export, list)
    assert ics_export[0] == 'BEGIN:VEVENT'
    assert ics_export[-1] == 'END:VEVENT'
    assert ics_export[-2] == 'TRANSP:TRANSPARENT'
    assert ics_export[-3] == f'SUMMARY:{gcal_event.summary}'
    assert ics_export[1] == "DTSTART:20210228T153000Z"

    # test timezone-awareness validator
    with pytest.raises(ValidationError):
        # dtstamp not timezone-aware
        VEvent(
            dtstart=start_datetime,
            dtend=end_datetime,
            dtstamp=dt.datetime(2021, 2, 28, 16, 30),
            summary="bla",
            uid="bla",
            transp="transparent",
        )


def test_ics_content():
    calendar_name = "Sonne"
    timezone = "Europe/Berlin"
    gcal_event1 = GoogleCalEvent(
        start=start_time, end=end_time, summary="event1"
    )
    gcal_event2 = GoogleCalEvent(
        start=start_time, end=end_time, summary="event2"
    )
    events = [gcal_event1, gcal_event2]

    ics_content = create_ics_content(gcal_events=events)

    assert isinstance(ics_content, list)
    # test number of lines: header 5 lines, footer 1 line, per event 8 --> 22 lines in total
    assert len(ics_content) == 22
    assert ics_content[0] == "BEGIN:VCALENDAR"
    assert ics_content[-1] == "END:VCALENDAR"
    assert "VERSION:2.0" in ics_content

    # assert that both events have the same DTSTAMP
    dtstamps = [line for line in ics_content if "DTSTAMP" in line]
    assert len(dtstamps) == 2
    assert dtstamps[0] == dtstamps[1]
