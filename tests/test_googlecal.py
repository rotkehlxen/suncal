from pydantic import ValidationError
from suncal.models.googlecal import GoogleCalTime
import pytest


def test_date_or_datetime_check():
    with pytest.raises(ValidationError):
        gtime = GoogleCalTime(date="1", dateTime="2")




