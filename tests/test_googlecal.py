from pydantic import ValidationError
from suncal.models.googlecal import GoogleCalTime, google_cal_summary
import pytest
import datetime as dt


def test_date_or_datetime_check():
    with pytest.raises(ValidationError):
        # supply only either date or datetime
        gtime = GoogleCalTime(date=dt.date.today(), dateTime=dt.datetime.now())

    with pytest.raises(ValidationError):
        # at least one date type has to be provided
        gtime = GoogleCalTime(date=None, dateTime=None)


def test_calendar_summary():
    summary = google_cal_summary("sunrise", dt.datetime(2012, 2, 1, 15, 30, 0))
    assert summary == "↑🌞 03:30 PM"

    summary = google_cal_summary("sunset", dt.datetime(2012, 2, 1, 15, 30, 0))
    assert summary == "↓🌞 03:30 PM"

    summary = google_cal_summary("goldenhour")
    assert summary == "📷 golden hour"

    with pytest.raises(AssertionError):
        # non-existing event
        summary = google_cal_summary("mond")

    with pytest.raises(AssertionError):
        # no time provided
        summary = google_cal_summary("sunrise")


