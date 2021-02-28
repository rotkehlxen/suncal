from pydantic import BaseModel, validator, root_validator
from typing import Optional
import datetime as dt


class GoogleCalTime(BaseModel):
    """
    Can fill the "start" or "end" required field of a GoogleCalEvent!
    Has three fields: date, dateTime and timeZone, however, not all of them are required at a time.

    need date for all day events and dateTime for timed events
    timeZone: IANA timezone db name, NOT required if dateTime contains a time offset
    """

    date: Optional[dt.date] = None
    dateTime: Optional[dt.datetime] = None
    timeZone: Optional[str] = None

    # make sure that either date OR dateTime is provided (but not both at the same time)
    @root_validator(pre=True)
    def date_or_dateTime_provided(cls, values):
        date, datetime = values.get('date'), values.get('dateTime')
        assert (date is None and datetime is not None) or (date is not None and datetime is None), \
            "You have to provide a date for all day events OR a datetime for timed events!"
        return values

    # TODO: The next two TODO items are not required for this particular application, as astral will always return ...
    # TODO: ... datetime objects with timezone offset:
    # TODO: 1. check for valid IANA timezone names
    # TODO: 2. check that timezone is provided when dateTime does not contain a timezone offset


class GoogleCalEvent(BaseModel):
    """ The only required parameters of a google cal event are start and end. 'summary' is the correct
      field name of the event title. Can add additional fields later on when needed. """
    start: GoogleCalTime
    end: GoogleCalTime
    summary: str

    def payload(self):
        """pydantic provides method json() that serializes our model, especially datetime objects are converted
        to the isoformat sring automatically! For example, if a is an instance of GoogleCalEvent, we get sth like

        a.json() = '{"start": {"date": null, "dateTime": "2011-11-04T00:05:23+04:00", "timeZone": null},
                     "end": {"date": null, "dateTime": "2011-11-05T00:05:23+04:00", "timeZone": null},
                     "summary": "Calender event"}'

        This is almost what we want! We only have to create a dict from this json string and maybe we have to remove
        all fields containing null values (but maybe not!). This should be implemented in the payload method.
        """
        pass


def google_cal_summary(event: str, time: Optional[dt.datetime] = None) -> str:
    """Create event summary. """

    assert event in ["sunrise", "sunset", "goldenhour"], "We only support events 'sunrise', 'sunset' and 'goldenhour'!"
    if event != "goldenhour":
        assert time is not None, "Provide argument 'time' (datetime object) for calender summary!"

    if event == "sunrise":
        # time in format "06:00 AM"
        time_str = time.strftime("%I:%M %p")
        return f"↑🌞 {time_str}"

    elif event == "sunset":
        time_str = time.strftime("%I:%M %p")
        return f"↓🌞 {time_str}"

    elif event == "goldenhour":
        return "📷 golden hour"
