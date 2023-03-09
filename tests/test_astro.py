import datetime as dt

from suncal.models.astro import Celestial
from suncal.utils import tz_aware_dt


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


def test_celestial_north_pole():
    """The current version of astral throws a ValueError for locations in which there is no actual sunrise,
    e.g. at the north pole. In that sitation we set start and end values of events to None."""

    timezone = "Europe/Berlin"
    date = dt.date.today()
    longitude = 0
    latitude = 90

    celestial = Celestial(
        timezone=timezone, date=date, longitude=longitude, latitude=latitude
    )

    assert not celestial.events['sunrise']['start']
    assert not celestial.events['sunrise']['end']
    assert not celestial.events['sunrise']['gcal_summary']


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
