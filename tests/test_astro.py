import datetime as dt

import pytest
from pydantic import ValidationError

from suncal.models.astro import CALC
from suncal.models.astro import CelestialBody
from suncal.models.astro import Location
from suncal.models.astro import MagicHour
from suncal.models.astro import MoonPhase
from suncal.models.astro import RiseSet
from suncal.models.astro import calculate_moon_phase
from suncal.utils import tz_aware_dt
from tests.test_data import CITIES


def test_location_class():
    location = Location(timezone='Europe/Berlin', longitude=10, latitude=20)

    assert location.timezone == 'Europe/Berlin'
    assert location.longitude == 10
    assert location.latitude == 20


def test_rise_set_class():
    timezone = 'Europe/Berlin'
    location = Location(timezone=timezone, longitude=0, latitude=0)
    event_time = tz_aware_dt(
        naive_datetime=dt.datetime.now(), timezone=timezone
    )

    # test sunrise
    sunrise = RiseSet(
        location=location,
        event_time=event_time,
        body=CelestialBody.SUN,
        rise=True,
    )

    assert sunrise.body == CelestialBody.SUN
    assert sunrise.event_time == event_time
    assert sunrise.rise
    assert sunrise.location == location

    # test moonset
    moonset = RiseSet(
        location=location,
        event_time=event_time,
        body=CelestialBody.MOON,
        rise=False,
    )

    assert moonset.body == CelestialBody.MOON
    assert moonset.event_time == event_time
    assert not moonset.rise
    assert moonset.location == location


def test_moon_phase_class():
    timezone = 'Europe/Berlin'
    event_time = tz_aware_dt(
        naive_datetime=dt.datetime.now(), timezone=timezone
    )
    moonphase = MoonPhase(timezone=timezone, event_time=event_time, phase_idx=3)
    assert moonphase.phase_idx == 3

    with pytest.raises(ValidationError):
        # there is no moon phase with phase_idx 4
        MoonPhase(timezone=timezone, event_time=event_time, phase_idx=4)


def test_moon_phase():
    timezone = "Europe/Berlin"
    date = dt.date(2023, 3, 15)

    moon_phase = calculate_moon_phase(date=date, timezone=timezone)

    assert moon_phase is not None
    assert moon_phase.phase_idx == 3
    assert moon_phase.timezone == "Europe/Berlin"


def test_rise_set_calculations():
    """
    Make sure that what we calculate here is within limits (+-3min) of the info on
    timeanddate.com
    """
    date = dt.date(2023, 3, 9)
    prec = dt.timedelta(minutes=3)

    for city in CITIES:
        location = Location(
            timezone=city['timezone'],
            longitude=city['long'],
            latitude=city['lat'],
        )
        for celestial_event in ['sunrise', 'sunset', 'moonrise', 'moonset']:

            tad_time = tz_aware_dt(
                dt.datetime.combine(date, city[celestial_event]),  # type: ignore
                city['timezone'],  # type: ignore
            )
            rise_set_event = CALC[celestial_event](date=date, location=location)

            assert rise_set_event is not None
            assert isinstance(rise_set_event, RiseSet)
            assert (
                tad_time - prec <= rise_set_event.event_time <= tad_time + prec
            )


def test_magic_hour_calculations():
    location = Location(
        timezone='Europe/Berlin', longitude=13.404954, latitude=52.520008
    )
    date = dt.date(2023, 3, 18)
    # reference values from timeanddate.com
    magic = {
        'golden_hour_morning': {'start': dt.time(5, 50), 'end': dt.time(6, 56)},
        'blue_hour_morning': {'start': dt.time(5, 24), 'end': dt.time(5, 50)},
        'golden_hour_evening': {
            'start': dt.time(17, 29),
            'end': dt.time(18, 35),
        },
        'blue_hour_evening': {'start': dt.time(18, 35), 'end': dt.time(19, 0)},
    }
    prec = dt.timedelta(minutes=4)

    for event in magic.keys():

        magic_hour = CALC[event](date, location)
        ref_start = tz_aware_dt(
            dt.datetime.combine(date, magic[event]['start']), location.timezone
        )
        ref_end = tz_aware_dt(
            dt.datetime.combine(date, magic[event]['end']), location.timezone
        )

        assert magic_hour is not None
        assert isinstance(magic_hour, MagicHour)
        assert ref_start - prec <= magic_hour.start <= ref_start + prec
        assert ref_end - prec <= magic_hour.end <= ref_end + prec
