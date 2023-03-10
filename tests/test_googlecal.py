import datetime as dt

import pytest
from pydantic import ValidationError

from suncal.models.googlecal import GoogleCalEvent
from suncal.models.googlecal import GoogleCalTime
from suncal.suncal import create_calendar_events
from suncal.utils import tz_aware_dt

now = dt.datetime.now()
today = dt.datetime.today()
time_zone = "Europe/Berlin"


def test_date_or_datetime_check():
    with pytest.raises(ValidationError):
        # supply only either date or datetime
        GoogleCalTime(date=dt.date.today(), dateTime=now, timeZone=time_zone)

    with pytest.raises(ValidationError):
        # at least one date type has to be provided
        GoogleCalTime(date=None, dateTime=None, timeZone=time_zone)


def test_timezone_added_if_datetime_non_aware():
    with pytest.raises(ValidationError):
        GoogleCalTime(dateTime=now)

    gcaltime = GoogleCalTime(dateTime=now, timeZone=time_zone)
    assert gcaltime.dateTime == now
    assert gcaltime.timeZone == time_zone


def test_transparency_validation():
    with pytest.raises(ValidationError):
        GoogleCalEvent(
            start=GoogleCalTime(date=today),
            end=GoogleCalTime(date=today),
            summary='summary',
            transparency="non-opaque",
        )


def test_transparency_default():
    event = GoogleCalEvent(
        start=GoogleCalTime(date=today),
        end=GoogleCalTime(date=today),
        summary='summary',
    )

    assert event.transparency == 'transparent'


def test_google_cal_event_payload():
    start = GoogleCalTime(
        dateTime=tz_aware_dt(
            dt.datetime(
                year=2021, month=2, day=28, hour=16, minute=30, second=0
            ),
            timezone=time_zone,
        )
    )
    end = GoogleCalTime(
        dateTime=tz_aware_dt(
            dt.datetime(
                year=2021, month=2, day=28, hour=17, minute=30, second=0
            ),
            timezone=time_zone,
        )
    )
    event = GoogleCalEvent(start=start, end=end, summary="test event")
    payload = event.payload()

    assert payload["start"]["date"] is None
    assert payload["start"]["dateTime"] == "2021-02-28T16:30:00+01:00"
    assert payload["start"]["timeZone"] is None
    assert payload["end"]["dateTime"] == "2021-02-28T17:30:00+01:00"
    assert payload["summary"] == "test event"


def test_create_calendar_events():

    from_date = dt.date(2021, 5, 1)
    to_date = dt.date(2021, 5, 3)
    longitude = 13.23
    latitude = 52.32

    gcal_event_list = create_calendar_events(
        event="sunrise",
        from_date=from_date,
        to_date=to_date,
        timezone=time_zone,
        longitude=longitude,
        latitude=latitude,
    )

    assert len(gcal_event_list) == 3
    assert all(
        isinstance(cal_event, GoogleCalEvent) for cal_event in gcal_event_list
    )

    # use the north pole as example for coordinates in which we expect an exception from astral
    latitude = 90
    longitude = 0

    gcal_event_list = create_calendar_events(
        event="sunrise",
        from_date=from_date,
        to_date=to_date,
        timezone=time_zone,
        longitude=longitude,
        latitude=latitude,
    )

    assert len(gcal_event_list) == 0
