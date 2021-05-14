import datetime as dt
import json
from typing import Dict
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pydantic import BaseModel  # pylint: disable=E0611
from pydantic import root_validator
from pydantic import validator


class GoogleCalTime(BaseModel):
    """
    Model for a google calendar time. Used to specify start and end of a google calendar event.
    """

    date: Optional[dt.date] = None  # for all-day events
    dateTime: Optional[dt.datetime] = None  # for timed events
    timeZone: Optional[
        str
    ] = None  # required only if provided dateTime is not aware

    @root_validator(pre=True)
    # make sure that either date OR dateTime is provided (but not both at the same time)  # pylint: disable=E0213
    def date_or_datetime_provided(cls, values):
        date, datetime = values.get("date"), values.get("dateTime")
        assert (date is None and datetime is not None) or (
            date is not None and datetime is None
        ), "You have to provide a date for all day events OR a datetime for timed events!"
        return values

    # if the root validator above fails, the following root validator is NOT executed
    @root_validator(pre=True)
    def timezone_provided_if_non_aware_datetime(
        cls, values
    ):  # pylint: disable=E0213
        datetime, timezone = values.get("dateTime"), values.get("timeZone")
        if datetime and (
            datetime.tzinfo is None or datetime.utcoffset() is None
        ):
            assert (
                timezone is not None
            ), "If the dateTime is unaware you have to provide a timeZone."
        return values


class GoogleCalEvent(BaseModel):
    """Model for google calendar event.

    The only required fields are 'start' and 'end'. More fields can be added when necessary."""

    start: GoogleCalTime  # required field
    end: GoogleCalTime  # required field
    summary: str  # title of event, optional
    transparency: str = (
        'transparent'  # sun calendar events are definitely no time blockers
    )

    @validator('transparency')
    def transparency_valid(cls, v):  # pylint: disable=E0213
        if v not in ['transparent', 'opaque']:
            raise ValueError(
                'Transparency of google calendar event can only be "transparent" or "opaque".'
            )
        return v.title()

    def payload(self):
        """pydantic provides method json() that serializes our model, especially datetime objects are converted
        to the isoformat sring automatically! For example, if a is an instance of GoogleCalEvent, we get sth like

        a.json() = '{"start": {"date": null, "dateTime": "2011-11-04T00:05:23+04:00", "timeZone": null},
                     "end": {"date": null, "dateTime": "2011-11-05T00:05:23+04:00", "timeZone": null},
                     "summary": "Calender event"}'
        We convert this json string back to a dictionary. This creates None type objects in places where we had string
        'null" before - however, this is accepted by the api client (tested).
        """
        return json.loads(self.json())


def get_sun_calendar_id(
    calendar_title: str, timezone: str, creds: Credentials
) -> str:

    all_calendars = request_calendars(creds=creds)
    # dict of calendars with matching title
    sun_calendars = {
        gcal_id: gcal_summary
        for (gcal_id, gcal_summary) in all_calendars.items()
        if gcal_summary == calendar_title
    }

    if len(sun_calendars) == 0:
        google_calendar_id = create_sun_calendar(
            calendar_title=calendar_title, timezone=timezone, creds=creds
        )
    else:
        google_calendar_id = sorted(list(sun_calendars.keys()))[0]

    if len(sun_calendars) > 1:
        print(f"You have more than one calendar with title {calendar_title}!")
        print(
            f"Will insert events into calendar {calendar_title} with id {google_calendar_id}."
        )

    return google_calendar_id


def request_calendars(creds: Credentials) -> Dict[str, str]:

    # TODO: what do we do in case we get no response?
    with build("calendar", "v3", credentials=creds) as service:

        # use calendar id as key and calendar summary as value in this dict (summary would be more handy as key,
        # but unfortunately calendar titles don"t have to be unique (verified!)
        calendars: Dict[str, str] = {}
        # response can have several pages (i.e. there is a max number of entries per page)
        page_token = None
        while True:
            calendar_list = (
                service.calendarList().list(pageToken=page_token).execute()
            )
            for entry in calendar_list['items']:
                calendars[entry['id']] = entry['summary']

            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

    return calendars


def create_sun_calendar(
    calendar_title: str, timezone: str, creds: Credentials
) -> str:

    with build("calendar", "v3", credentials=creds) as service:
        calendar = {"summary": calendar_title, "timeZone": timezone}

        created_calendar = service.calendars().insert(body=calendar).execute()

    return created_calendar["id"]
