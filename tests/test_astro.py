import datetime as dt

import pytest
from pydantic import ValidationError

from suncal.models.astro import CALC
from suncal.models.astro import CelestialBody
from suncal.models.astro import Location
from suncal.models.astro import MoonPhase
from suncal.models.astro import RiseSet
from suncal.models.astro import calculate_moon_phase
from suncal.utils import tz_aware_dt


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

    # locations, date 9.3.2023, sun/moon rise & set according to timeanddate.com (tad) in local time
    berlin = {
        'lat': 52.520008,
        'long': 13.404954,
        'timezone': 'Europe/Berlin',
        'sunrise': dt.time(6, 35),
        'sunset': dt.time(17, 59),
        'moonrise': dt.time(20, 17),
        'moonset': dt.time(7, 26),
    }

    redwoodcity = {
        'lat': 37.4848,
        'long': -122.2281,
        'timezone': 'US/Pacific',
        'sunrise': dt.time(6, 28),
        'sunset': dt.time(18, 10),
        'moonrise': dt.time(20, 33),
        'moonset': dt.time(7, 40),
    }

    punta_arenas = {
        'lat': -53.163833,
        'long': -70.917068,
        'timezone': 'America/Santiago',
        'sunrise': dt.time(7, 24),
        'sunset': dt.time(20, 22),
        'moonrise': dt.time(21, 12),
        'moonset': dt.time(9, 33),
    }
    maputo = {
        'lat': -25.966667,
        'long': 32.583333,
        'timezone': 'Africa/Johannesburg',
        'sunrise': dt.time(5, 47),
        'sunset': dt.time(18, 12),
        'moonrise': dt.time(19, 28),
        'moonset': dt.time(7, 15),
    }

    auckland = {
        'lat': -36.848461,
        'long': 174.763336,
        'timezone': 'Pacific/Auckland',
        'sunrise': dt.time(7, 13),
        'sunset': dt.time(19, 49),
        'moonrise': dt.time(20, 46),
        'moonset': dt.time(8, 23),
    }

    cities = [berlin, redwoodcity, punta_arenas, maputo, auckland]

    for city in cities:
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
            assert (
                tad_time - prec <= rise_set_event.event_time <= tad_time + prec
            )
