import datetime as dt

from suncal.fileio import ics_filename


def test_ics_filename():
    name = ics_filename(
        event_name="golden-hour-morning",
        local_time_now=dt.datetime(2021, 5, 10, 10, 0, 0),
    )
    assert name == "Golden-Hour-Morning_20210510_100000.ics"
