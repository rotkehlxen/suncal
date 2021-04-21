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
    assert isinstance(celestial.event["sunrise"]["start"], dt.datetime)

    # test the gcal summary
    assert "↑🌞" in celestial.event['sunrise']['gcal_summary']
    assert "AM" in celestial.event['sunrise']['gcal_summary']
    assert "↓🌞" in celestial.event['sunset']['gcal_summary']
    assert celestial.event['goldenhour']['gcal_summary'] == "📷 golden hour"

    # end of goldenhour
    end_golden_hour = celestial.event["goldenhour"]["end"]
    assert isinstance(end_golden_hour, dt.datetime)
    assert end_golden_hour.date() == celestial.date

    # reset the date: calculations are updated as well!
    celestial.date = date + dt.timedelta(days=3)
    new_end_golden_hour = celestial.event["goldenhour"]["end"]
    assert new_end_golden_hour.date() == date + dt.timedelta(days=3)
    assert end_golden_hour != new_end_golden_hour
