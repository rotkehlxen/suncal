from pydantic import ValidationError
from suncal.models.googlecal import GoogleCalTime
import pytest
import datetime as dt


def test_date_or_datetime_check():
    with pytest.raises(ValidationError):
        # supply only either date or datetime
        gtime = GoogleCalTime(date=dt.date.today(), dateTime=dt.datetime.now())

    with pytest.raises(ValidationError):
        # at least one date type has to be provided
        gtime = GoogleCalTime(date=None, dateTime=None)



