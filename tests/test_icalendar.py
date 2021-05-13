import datetime as dt

import pytest
from pydantic import ValidationError

from suncal.date_utils import create_timezone_aware_datetime
from suncal.models.googlecal import GoogleCalEvent
from suncal.models.googlecal import GoogleCalTime
from suncal.models.icalendar import VCalendar
from suncal.models.icalendar import VEvent


def test_vcalendar():
    vcal = VCalendar(x_wr_calname="Sonne", x_wr_timezone="Europe/Berlin")

    assert vcal.x_wr_timezone == "Europe/Berlin"
    assert vcal.method == "PUBLISH"
    assert vcal.prodid == "PLACEHOLDER"
    assert vcal.x_wr_calname == "Sonne"
    assert vcal.cascale == "GREGORIAN"

    assert VCalendar.footer() == ["END:VCALENDAR"]
    assert vcal.footer() == ["END:VCALENDAR"]
    assert "METHOD:PUBLISH" in vcal.header()
    assert vcal.header()[2] == "VERSION:2.0"


def test_vevent():

    # test creation of VEvent from GoogleCalTime
    start_datetime = create_timezone_aware_datetime(
        year=2021,
        month=2,
        day=28,
        hour=16,
        minute=30,
        second=0,
        timezone="Europe/Berlin",
    )

    end_datetime = create_timezone_aware_datetime(
        year=2021,
        month=2,
        day=28,
        hour=17,
        minute=30,
        second=0,
        timezone="Europe/Berlin",
    )
    start_time = GoogleCalTime(dateTime=start_datetime)
    end_time = GoogleCalTime(dateTime=end_datetime)

    gcal_event = GoogleCalEvent(
        start=start_time, end=end_time, summary="event_summary"
    )

    now = dt.datetime.now(dt.timezone.utc)
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
