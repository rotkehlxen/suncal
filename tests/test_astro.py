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
    assert "↑🌞" in celestial.events['sunrise']['gcal_summary']
    assert "AM" in celestial.events['sunrise']['gcal_summary']
    assert "↓🌞" in celestial.events['sunset']['gcal_summary']
    assert (
        celestial.events['golden-hour-morning']['gcal_summary']
        == "📷 Golden Hour"
    )
    assert (
        celestial.events['golden-hour-evening']['gcal_summary']
        == "📷 Golden Hour"
    )

    # end of goldenhour
    end_golden_hour = celestial.events["golden-hour-morning"]["end"]
    assert isinstance(end_golden_hour, dt.datetime)
    assert end_golden_hour.date() == celestial.date

    # reset the date: calculations are updated as well!
    celestial.date = date + dt.timedelta(days=3)
    new_end_golden_hour = celestial.events["golden-hour-morning"]["end"]
    assert new_end_golden_hour.date() == date + dt.timedelta(days=3)
    assert end_golden_hour != new_end_golden_hour


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

    assert (
        celestial.events['golden-hour-morning']['gcal_summary']
        == "📷 Golden Hour"
    )
    assert not celestial.events['golden-hour-morning']['start']
