import datetime as dt

from suncal.models.astro import Celestial


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
