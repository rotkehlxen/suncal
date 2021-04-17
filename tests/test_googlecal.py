from pydantic import ValidationError
from suncal.models.googlecal import GoogleCalTime, GoogleCalEvent, google_cal_summary
from suncal.utils import create_timezone_aware_datetime
import pytest
import datetime as dt


def test_date_or_datetime_check():
    with pytest.raises(ValidationError):
        # supply only either date or datetime
        GoogleCalTime(date=dt.date.today(), dateTime=dt.datetime.now())

    with pytest.raises(ValidationError):
        # at least one date type has to be provided
        GoogleCalTime(date=None, dateTime=None)


def test_google_cal_event_payload():
    start = GoogleCalTime(dateTime=create_timezone_aware_datetime(year=2021, month=2, day=28, hour=16,
                                                                  minute=30, second=0, timezone='Europe/Berlin'))
    end = GoogleCalTime(dateTime=create_timezone_aware_datetime(year=2021, month=2, day=28, hour=17, minute=30,
                                                                second=0, timezone='Europe/Berlin'))
    event = GoogleCalEvent(start=start, end=end, summary="test event")
    payload = event.payload()

    assert payload['start']['date'] is None
    assert payload['start']['dateTime'] == '2021-02-28T16:30:00+01:00'
    assert payload['start']['timezone'] is None
    assert payload['end']['dateTime'] == '2021-02-28T17:30:00+01:00'
    assert payload['summary'] == 'test event'






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


