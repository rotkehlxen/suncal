import datetime as dt
import pytest
import numpy as np
import pytz
from skyfield import almanac
from skyfield import api as skyfield_api
from skyfield.timelib import Time

from suncal.models.astro import Celestial
from suncal.models.astro import extract_moon_phase
from suncal.models.astro import rise_set_dict
from suncal.models.astro import Location, RiseSet, MoonPhase, Planet
from suncal.utils import tz_aware_dt
from pydantic import ValidationError

def test_location_class():
    location = Location(timezone='Europe/Berlin', longitude = '10', latitude = 20)

    assert location.timezone == 'Europe/Berlin'
    assert location.longitude == 10
    assert location.latitude == 20


def test_rise_set_class():
    timezone = 'Europe/Berlin'
    location = Location(timezone=timezone, longitude=0, latitude=0)
    event_time = tz_aware_dt(naive_datetime=dt.datetime.now(), timezone=timezone)

    # test sunrise
    sunrise = RiseSet(location=location, event_time=event_time, planet=Planet.SUN, rise=True)

    assert sunrise.planet == Planet.SUN
    assert sunrise.event_time == event_time
    assert sunrise.rise
    assert sunrise.location == location

    # test moonset
    moonset = RiseSet(location=location, event_time=event_time, planet=Planet.MOON, rise=False)

    assert moonset.planet == Planet.MOON
    assert moonset.event_time == event_time
    assert not moonset.rise
    assert moonset.location == location


def test_moon_phase_class():
    timezone = 'Europe/Berlin'
    location = Location(timezone=timezone, longitude=0, latitude=0)
    event_time = tz_aware_dt(naive_datetime=dt.datetime.now(), timezone=timezone)

    moonphase = MoonPhase(location=location, event_time= event_time, phase_idx=3)
    assert moonphase.phase_idx == 3

    with pytest.raises(ValidationError):
        # there is no moon phase with phase_idx 4
        MoonPhase(location=location, event_time=event_time, phase_idx=4)


def test_celestial():
    timezone = "Europe/Berlin"
    date = dt.date.today()
    longitude = "30"
    latitude = 50

    celestial = Celestial(
        timezone=timezone, date=date, longitude=longitude, latitude=latitude
    )

    # pydantic converts the non-float inputs (str an int) to float
    assert isinstance(celestial.longitude, float)
    assert isinstance(celestial.latitude, float)

    # start of sunrise can be obtained like this
    assert isinstance(celestial.events["sunrise"]["start"], dt.datetime)

    # test the gcal summary
    assert "🌞↑" in celestial.events['sunrise']['gcal_summary']
    assert "AM" in celestial.events['sunrise']['gcal_summary']
    assert "🌞↓" in celestial.events['sunset']['gcal_summary']


def test_extract_moon_phase():
    ts = skyfield_api.load.timescale()
    # create a skyfield Time object in a sneaky way
    time = ts.now()
    # we have to set tt to an array, because that is the kind of object we get from phase calculation
    skyfield_t = Time(tt=np.array([time.tt]), ts=ts)
    skyfield_y = np.array([0])
    timezone = 'Europe/Berlin'

    phase_name, phase_symbol, phase_time = extract_moon_phase(
        skyfield_t, skyfield_y, timezone
    )

    assert phase_name == "New Moon"
    assert phase_symbol == "🌚"
    assert isinstance(phase_time, dt.datetime)
    assert phase_time.date() == dt.date.today()


def test_moon_phase():
    timezone = "Europe/Berlin"
    date = dt.date(2023, 3, 15)
    lat = 52.520008
    long = 13.404954

    celestial = Celestial(
        timezone=timezone, date=date, longitude=long, latitude=lat
    )

    assert celestial.events['moonphase']['start'] == date
    assert 'Last Quarter' in celestial.events['moonphase']['gcal_summary']


def test_celestial_north_pole():

    timezone = "Europe/Berlin"
    date = dt.date.today()
    longitude = 0
    latitude = 90

    celestial = Celestial(
        timezone=timezone, date=date, longitude=longitude, latitude=latitude
    )

    assert 'sunrise' not in celestial.events.keys()


def test_celestial_calculations():
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
        'sunrise_tad': dt.time(6, 35),
        'sunset_tad': dt.time(17, 59),
        'moonrise_tad': dt.time(20, 17),
        'moonset_tad': dt.time(7, 26),
    }

    redwoodcity = {
        'lat': 37.4848,
        'long': -122.2281,
        'timezone': 'US/Pacific',
        'sunrise_tad': dt.time(6, 28),
        'sunset_tad': dt.time(18, 10),
        'moonrise_tad': dt.time(20, 33),
        'moonset_tad': dt.time(7, 40),
    }

    punta_arenas = {
        'lat': -53.163833,
        'long': -70.917068,
        'timezone': 'America/Santiago',
        'sunrise_tad': dt.time(7, 24),
        'sunset_tad': dt.time(20, 22),
        'moonrise_tad': dt.time(21, 12),
        'moonset_tad': dt.time(9, 33),
    }
    maputo = {
        'lat': -25.966667,
        'long': 32.583333,
        'timezone': 'Africa/Johannesburg',
        'sunrise_tad': dt.time(5, 47),
        'sunset_tad': dt.time(18, 12),
        'moonrise_tad': dt.time(19, 28),
        'moonset_tad': dt.time(7, 15),
    }

    auckland = {
        'lat': -36.848461,
        'long': 174.763336,
        'timezone': 'Pacific/Auckland',
        'sunrise_tad': dt.time(7, 13),
        'sunset_tad': dt.time(19, 49),
        'moonrise_tad': dt.time(20, 46),
        'moonset_tad': dt.time(8, 23),
    }

    cities = [berlin, redwoodcity, punta_arenas, maputo, auckland]

    for city in cities:

        celestial = Celestial(
            timezone=city['timezone'],
            date=date,
            longitude=city['long'],
            latitude=city['lat'],
        )
        # test sunrise
        sunrise = tz_aware_dt(
            dt.datetime.combine(date, city['sunrise_tad']), city['timezone']  # type: ignore
        )
        assert (
            sunrise - prec
            <= celestial.events['sunrise']['start']
            <= sunrise + prec
        )

        # test sunset
        sunset = tz_aware_dt(
            dt.datetime.combine(date, city['sunset_tad']), city['timezone']  # type: ignore
        )
        assert (
            sunset - prec
            <= celestial.events['sunset']['start']
            <= sunset + prec
        )

        # test moonrise
        moonrise = tz_aware_dt(
            dt.datetime.combine(date, city['moonrise_tad']), city['timezone']  # type: ignore
        )
        assert (
            moonrise - prec
            <= celestial.events['moonrise']['start']
            <= moonrise + prec
        )

        # test moonset
        moonset = tz_aware_dt(
            dt.datetime.combine(date, city['moonset_tad']), city['timezone']  # type: ignore
        )
        assert (
            moonset - prec
            <= celestial.events['moonset']['start']
            <= moonset + prec
        )


def test_rise_set_dict():
    ts = skyfield_api.load.timescale()
    eph = skyfield_api.load('de421.bsp')
    # 1. missing moon rise event is added
    # The moon does not rise in Berlin on that day
    berlin_time = pytz.timezone('Europe/Berlin')
    berlin = skyfield_api.wgs84.latlon(52, 14.32)
    t0 = berlin_time.localize(dt.datetime(2023, 3, 12, 0, 0, 0))
    t1 = berlin_time.localize(dt.datetime(2023, 3, 12, 23, 59, 59, 999))

    t0_sky = ts.from_datetime(t0)
    t1_sky = ts.from_datetime(t1)

    t, y = almanac.find_discrete(
        t0_sky, t1_sky, almanac.risings_and_settings(eph, eph['moon'], berlin)
    )

    assert len(t) == 1
    assert len(y) == 1
    # the moon only sets on that day
    assert 0 in y

    events = rise_set_dict(t, y, 'Europe/Berlin')
    assert isinstance(events, dict)
    assert events['rise'] is None
    assert isinstance(events['set'], dt.datetime)
    assert events['set'].tzinfo is not None

    # 2. missing rise and set is added with None (function can handle empty return objects)

    # Hammerfest in the North of Norway experiences polar nights and midnight suns
    hammerfest = skyfield_api.wgs84.latlon(70.66336, 23.68209)
    t0 = ts.utc(2023, 1, 1, 0, 0)
    t1 = ts.utc(2023, 1, 1, 23, 59)

    t, y = almanac.find_discrete(
        t0, t1, almanac.sunrise_sunset(eph, hammerfest)
    )

    # polar night on the 1st of Jan, so no sunrise and no sunset
    assert len(t) == 0
    assert len(y) == 0
    # expected return types of the almanac calculation
    assert isinstance(y, np.ndarray)
    assert isinstance(t, Time)

    events = rise_set_dict(t, y, 'utc')
    assert isinstance(events, dict)
    assert events['set'] is None
    assert events['rise'] is None
