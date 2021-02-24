from pydantic import ValidationError
from suncal.models.googlecal import GoogleCalTime
import pytest


def test_date_or_datetime_check():
    with pytest.raises(ValidationError):
        # supply only either date or datetime
        gtime = GoogleCalTime(date="2020-02-09", dateTime="sometime")

    with pytest.raises(ValidationError):
        # at least one date type has to be provided
        gtime = GoogleCalTime(date=None, dateTime=None)

def test_date_format():
    with pytest.raises(ValidationError):
        # here we have format yyyy-dd-mm, but we demand yyyy-mm-dd
        gtime = GoogleCalTime(date="2020-30-01")

    with pytest.raises(ValidationError):
        # years past 2999 are not allowed
        gtime = GoogleCalTime(date="3000-01-30")




