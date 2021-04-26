import datetime as dt

from suncal.utils import create_timezone_aware_datetime
from suncal.utils import date_range


def test_date_range():
    # test transition between years
    from_date = dt.date(2020, 12, 30)
    to_date = dt.date(2021, 1, 2)

    out = [
        dt.date(2020, 12, 30),
        dt.date(2020, 12, 31),
        dt.date(2021, 1, 1),
        dt.date(2021, 1, 2),
    ]
    assert out == date_range(from_date, to_date)

    # check if leap years are accounted for
    from_date = dt.date(2024, 2, 28)
    to_date = dt.date(2024, 3, 1)

    out = [dt.date(2024, 2, 28), dt.date(2024, 2, 29), dt.date(2024, 3, 1)]
    assert out == date_range(from_date, to_date)

    # check that we get list of one date if from and to are the same
    from_date = dt.date(2020, 12, 30)
    to_date = dt.date(2020, 12, 30)

    out = [dt.date(2020, 12, 30)]
    assert out == date_range(from_date, to_date)


def test_create_timezone_aware_datetime():
    my_time = create_timezone_aware_datetime(
        year=2021,
        month=4,
        day=17,
        hour=16,
        minute=30,
        second=0,
        timezone="Europe/Berlin",
    )
    assert isinstance(my_time, dt.datetime)
    assert my_time.year == 2021
    assert my_time.second == 0
    assert my_time.month == 4
    assert my_time.hour == 16
    # "CET" in daylight saving time: "CEST"
    assert my_time.tzname() == "CEST"
    # utc offset of 2h because of daylight saving time
    assert my_time.utcoffset() == dt.timedelta(seconds=7200)
    # daylight saving time adjustment of 1h
    assert my_time.dst() == dt.timedelta(seconds=3600)