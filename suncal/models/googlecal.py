import datetime as dt
import json
from typing import Dict
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pydantic import BaseModel  # pylint: disable=E0611
from pydantic import root_validator


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
    def date_or_dateTime_provided(cls, values):  # pylint: disable=E0213
        date, datetime = values.get("date"), values.get("dateTime")
        assert (date is None and datetime is not None) or (
            date is not None and datetime is None
        ), "You have to provide a date for all day events OR a datetime for timed events!"
        return values

    # TODO: The next two TODO items are not required for this particular application, as astral will always return ...
    # TODO: ... datetime objects with timezone offset:
    # TODO: 1. check for valid IANA timezone names
    # TODO: 2. check that timezone is provided when dateTime does not contain a timezone offset


class GoogleCalEvent(BaseModel):
    """The only required parameters of a google cal event are start and end. 'summary' is the correct
    field name of the event title. Can add additional fields later on when needed."""

    start: GoogleCalTime
    end: GoogleCalTime
    summary: str

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


def create_calendar_if_not_exists(
    calendar_id: str, timezone: str, creds: Credentials
) -> Optional[str]:
    # TODO: I do not know if we have to return this google calendar id
    if not sun_calendar_exists(calendar_id, creds):
        gcal_id = create_sun_calendar(calendar_id, timezone, creds)
        return gcal_id
    else:
        return None


def sun_calendar_exists(calendar_id: str, creds: Credentials) -> Optional[str]:

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
            for calendar_list_entry in calendar_list['items']:
                calendars[calendar_list_entry['id']] = calendar_list_entry[
                    'summary'
                ]

            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

        # get sub dict where the value matches our [calendar_id]
        sun_calendars = {
            gcal_id: gcal_summary
            for (gcal_id, gcal_summary) in calendars.items()
            if gcal_summary == calendar_id
        }
        if len(sun_calendars) > 1:
            print(f"You have more than one calendar with title {calendar_id}!")
            print(
                f"Will use the first calendar that was detected to insert events!"
            )

        if len(sun_calendars) == 0:
            return None
        else:
            return sorted(list(sun_calendars.keys()))[0]


def create_sun_calendar(
    calendar_id: str, timezone: str, creds: Credentials
) -> str:

    # TODO: I do not know whether we will need the returned id!
    with build("calendar", "v3", credentials=creds) as service:
        calendar = {"summary": calendar_id, "timeZone": timezone}

        created_calendar = service.calendars().insert(body=calendar).execute()

    return created_calendar["id"]
