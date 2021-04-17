import datetime as dt

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
