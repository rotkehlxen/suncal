from pydantic import BaseModel, validator, root_validator
from typing import Optional


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

    # make sure that either date OR dateTime is provided
    @root_validator(pre=True)
    def date_or_dateTime_provided(cls, values):
        date, datetime = values.get('date'), values.get('dateTime')
        assert date is None or datetime is None, "You have to provide a date for all day events or a datetime for " \
                                                 "timed events"
        return values

