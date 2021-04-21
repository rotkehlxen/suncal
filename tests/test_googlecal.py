import datetime as dt

import pytest
from pydantic import ValidationError

from suncal.models.googlecal import GoogleCalEvent
from suncal.models.googlecal import GoogleCalTime
from suncal.utils import create_timezone_aware_datetime


def test_date_or_datetime_check():
    with pytest.raises(ValidationError):
        # supply only either date or datetime
        GoogleCalTime(date=dt.date.today(), dateTime=dt.datetime.now())

    with pytest.raises(ValidationError):
        # at least one date type has to be provided
        GoogleCalTime(date=None, dateTime=None)


def test_google_cal_event_payload():
    start = GoogleCalTime(
        dateTime=create_timezone_aware_datetime(
            year=2021,
            month=2,
            day=28,
            hour=16,
            minute=30,
            second=0,
            timezone="Europe/Berlin",
        )
    )
    end = GoogleCalTime(
        dateTime=create_timezone_aware_datetime(
            year=2021,
            month=2,
            day=28,
            hour=17,
            minute=30,
            second=0,
            timezone="Europe/Berlin",
        )
    )
    event = GoogleCalEvent(start=start, end=end, summary="test event")
    payload = event.payload()

    assert payload["start"]["date"] is None
    assert payload["start"]["dateTime"] == "2021-02-28T16:30:00+01:00"
    assert payload["start"]["timeZone"] is None
    assert payload["end"]["dateTime"] == "2021-02-28T17:30:00+01:00"
    assert payload["summary"] == "test event"

