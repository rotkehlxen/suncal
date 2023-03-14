import datetime as dt

from suncal.utils import aware_datetime_to_ical_date_with_utc_time
from suncal.utils import create_batches
from suncal.utils import date_range
from suncal.utils import time_range_of_date
from suncal.utils import tz_aware_dt


def test_time_range_of_date():
    date = dt.date(2023, 3, 14)
    timezone = 'Europe/Berlin'

    start = dt.datetime(2023, 3, 14, 0, 0, 0, 0)
    end = dt.datetime(2023, 3, 14, 23, 59, 59, int(1e6 - 1))

    s, e = time_range_of_date(date=date, timezone=timezone)

    assert s == tz_aware_dt(start, timezone)
    assert e == tz_aware_dt(end, timezone)


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
    my_time = tz_aware_dt(
        dt.datetime(year=2021, month=4, day=17, hour=16, minute=30, second=0),
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


def test_ical_datetime():
    # create datetime in Europe/Berlin and convert to ical format
    datetime_berlin = tz_aware_dt(
        dt.datetime(year=2021, month=4, day=17, hour=16, minute=30, second=0),
        timezone="Europe/Berlin",
    )

    ical_string = aware_datetime_to_ical_date_with_utc_time(datetime_berlin)
    assert ical_string == "20210417T143000Z"

    # create datetime in UTC and see check that the time is unaffected (only the format)
    datetime_utc = tz_aware_dt(
        dt.datetime(year=2021, month=4, day=17, hour=16, minute=30, second=0),
        timezone="UTC",
    )

    ical_string = aware_datetime_to_ical_date_with_utc_time(datetime_utc)
    assert ical_string == "20210417T163000Z"


def test_create_batches():
    mylist = list(range(0, 8))
    batches = create_batches(mylist, batch_size=3)

    assert batches == [[0, 1, 2], [3, 4, 5], [6, 7]]
