from pydantic import BaseModel, validator, root_validator
from typing import Optional
import re


class GoogleCalEvent(BaseModel):
    pass


class GoogleCalTime(BaseModel):
    """
    Can fill the "start" or "end" required field of a GoogleCalEvent!
    Has three fields: date, dateTime and timeZone, however, not all of them are required at a time.

    date: "yyyy-mm-dd" for all day events
    dateTime: isoformat, for timed events --> event needs either date OR dateTime!
    timeZone: IANA timezone db name, NOT required if dateTime contains a time offset
    """

    date: Optional[str] = None
    dateTime: Optional[str] = None
    timeZone: Optional[str] = None

    # make sure that either date OR dateTime is provided (but not both at the same time)
    @root_validator(pre=True)
    def date_or_dateTime_provided(cls, values):
        date, datetime = values.get('date'), values.get('dateTime')
        assert (date is None and datetime is not None) or (date is not None and datetime is None), \
            "You have to provide a date for all day events OR a datetime for timed events!"
        return values

    # guarantee that date has format "yyyy-mm-dd" (if provided)
    @validator('date')
    def check_date_format(cls, val):
        # only accept dates of the 3rd chiliad :-)
        assert val is None or re.match(r"^2\d{3}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])$", val) is not None, \
            "Date has to be of format 'yyyy-mm-dd'!"



