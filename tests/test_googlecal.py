import datetime as dt

import pytest
from pydantic import ValidationError

from suncal.models.astro import CelestialBody
from suncal.models.astro import Location
from suncal.models.astro import MoonPhase
from suncal.models.astro import RiseSet
from suncal.models.googlecal import GoogleCalEvent
from suncal.models.googlecal import GoogleCalTime
from suncal.suncal import create_calendar_events
from suncal.utils import tz_aware_dt

now = dt.datetime.now()
today = dt.date.today()
time_zone = "Europe/Berlin"


# tests on GoogleCalTime
def test_google_cal_time():
    gtime = GoogleCalTime(datetime=now, timezone=time_zone)
    # field names are NOT the alias names
    assert gtime.datetime == now
    assert gtime.timezone == time_zone
    # also the schema does not contain alias field names by default
    assert 'datetime' in gtime.model_dump().keys()
    # but we can configure the schema to use the alias names
    assert 'dateTime' in gtime.model_dump(by_alias=True).keys()
    assert 'timeZone' in gtime.model_dump(by_alias=True).keys()


def test_date_or_datetime_check():
    with pytest.raises(ValidationError):
        # supply only either date or datetime
        GoogleCalTime(date=today, datetime=now, timezone=time_zone)

    with pytest.raises(ValidationError):
        # at least one date type has to be provided
        GoogleCalTime(date=None, datetime=None, timezone=time_zone)


def test_timezone_added_if_datetime_non_aware():
    with pytest.raises(ValidationError):
        GoogleCalTime(datetime=now)

    gcaltime = GoogleCalTime(datetime=now, timezone=time_zone)
    assert gcaltime.datetime == now
    assert gcaltime.timezone == time_zone

    with pytest.raises(ValidationError):
        gcaltime = GoogleCalTime(date=today)


# tests on GoogleCalEvent
def test_start_and_end_match():
    # Either use datetime or date in start and end
    with pytest.raises(ValidationError):
        GoogleCalEvent(
            start=GoogleCalTime(date=today, timezone=time_zone),
            end=GoogleCalTime(datetime=now, timezone=time_zone),
            summary='bla',
        )


def test_end_date_larger_start_date():
    with pytest.raises(ValidationError):
        GoogleCalEvent(
            start=GoogleCalTime(date=today, timezone=time_zone),
            end=GoogleCalTime(date=today, timezone=time_zone),
            summary='bla',
        )


def test_gcal_event_from_celestial_event():
    location = Location(timezone=time_zone, longitude=0, latitude=0)
    moon_phase = MoonPhase(
        timezone=time_zone,
        event_time=tz_aware_dt(now, timezone=time_zone),
        phase_idx=2,
    )

    gcal_event = GoogleCalEvent.from_celestial_event(moon_phase)

    assert gcal_event.start.date == now.date()
    assert gcal_event.start.datetime is None
    assert gcal_event.end.date == now.date() + dt.timedelta(days=1)
    assert "Full Moon" in gcal_event.summary
    assert "🌝" in gcal_event.summary

    sunrise = RiseSet(
        location=location,
        event_time=tz_aware_dt(now, timezone=time_zone),
        rise=True,
        body=CelestialBody.SUN,
    )

    gcal_event = GoogleCalEvent.from_celestial_event(sunrise)

    assert gcal_event.start.date is None
    assert gcal_event.start.datetime == tz_aware_dt(now, timezone=time_zone)
    assert gcal_event.end.datetime == tz_aware_dt(now, timezone=time_zone)
    assert '🌞' in gcal_event.summary
    assert '↑' in gcal_event.summary


def test_transparency_validation():
    with pytest.raises(ValidationError):
        GoogleCalEvent(
            start=GoogleCalTime(date=today, timezone=time_zone),
            end=GoogleCalTime(
                date=today + dt.timedelta(days=1), timezone=time_zone
            ),
            summary='summary',
            transparency="non-opaque",
        )


def test_transparency_default():
    event = GoogleCalEvent(
        start=GoogleCalTime(date=today, timezone=time_zone),
        end=GoogleCalTime(
            date=today + dt.timedelta(days=1), timezone=time_zone
        ),
        summary='summary',
    )

    assert event.transparency == 'transparent'


def test_google_cal_event_payload():
    start = GoogleCalTime(
        datetime=tz_aware_dt(
            dt.datetime(
                year=2021, month=2, day=28, hour=16, minute=30, second=0
            ),
            timezone=time_zone,
        )
    )
    end = GoogleCalTime(
        datetime=tz_aware_dt(
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

    location = Location(
        timezone=time_zone, longitude=longitude, latitude=latitude
    )

    gcal_event_list = create_calendar_events(
        event="sunrise",
        from_date=from_date,
        to_date=to_date,
        location=location,
    )

    assert len(gcal_event_list) == 3
    assert all(
        isinstance(cal_event, GoogleCalEvent) for cal_event in gcal_event_list
    )

    # use the North Pole as example for coordinates in which we don't expect a sunrise in May
    latitude = 90
    longitude = 0

    location = Location(
        timezone=time_zone, longitude=longitude, latitude=latitude
    )

    gcal_event_list = create_calendar_events(
        event="sunrise",
        from_date=from_date,
        to_date=to_date,
        location=location,
    )

    assert len(gcal_event_list) == 0
