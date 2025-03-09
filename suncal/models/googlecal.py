import datetime as dt
import json
import sys

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import BaseModel  # pylint: disable=E0611
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator
from skyfield.almanac import MOON_PHASES
from typing_extensions import Self

from suncal.models.astro import MOON_PHASE_SYMBOLS
from suncal.models.astro import CelestialBody
from suncal.models.astro import MagicHour
from suncal.models.astro import MoonPhase
from suncal.models.astro import RiseSet
from suncal.utils import create_batches


class GoogleCalTime(BaseModel):
    """
    Model for a Google Calendar time. Used to specify start and end of a Google Calendar event.
    """

    model_config = ConfigDict(populate_by_name=True)
    date: dt.date | None = None  # for all-day events
    datetime: dt.datetime | None = Field(
        alias='dateTime', default=None
    )  # for timed events
    timezone: str | None = Field(
        alias='timeZone', default=None
    )  # required only if provided dateTime is not aware

    @model_validator(mode='after')
    def date_or_datetime_provided(self) -> Self:
        """
        Validate that either date OR datetime is provided (and never both at the same time).
        """
        if (self.date is None and self.datetime is None) or (
            self.date is not None and self.datetime is not None
        ):
            raise ValueError(
                "You have to provide a date for all day events OR a datetime for timed events!"
            )
        return self

    @model_validator(mode='after')
    def timezone_provided_if_non_aware_datetime(self) -> Self:
        """
        Validate that timezone is provided if datetime is not aware of if date was specified instead of datetime.
        """
        if self.timezone is None:
            if self.datetime and (
                self.datetime.tzinfo is None
                or self.datetime.utcoffset() is None
            ):
                raise ValueError(
                    "If the datetime is unaware you have to provide a timezone"
                )
            if self.date:
                raise ValueError(
                    "Always provide a timezone if you specify date instead of datetime."
                )
        return self


class GoogleCalEvent(BaseModel):
    """Model for Google Calendar event.

    The only required fields are 'start' and 'end'. More fields can be added when necessary.
    """

    start: GoogleCalTime  # required field
    end: GoogleCalTime  # required field
    summary: str  # title of event, optional
    transparency: str = (
        'transparent'  # sun calendar events are definitely no time blockers
    )

    @model_validator(mode='after')
    def start_and_end_compatible(self) -> Self:
        """
        If start is defined by a date, end has to be defined by date also. Same for defintion of start and end by
        datetime.
        """
        if self.start.datetime is None and self.end.datetime is not None:
            raise ValueError(
                "If start has a date, end needs to have a date also."
            )
        if self.start.date is None and self.end.date is not None:
            raise ValueError(
                "If start has a datetime, end needs to have a datetime also."
            )
        return self

    @model_validator(mode='after')
    def end_date_larger_than_start_date(self) -> Self:
        """
        Validate that end date is larger than start date.
        """
        if self.start.date and self.end.date:
            if not self.end.date > self.start.date:
                raise ValueError(
                    "End is the exclusive(!) end date of the event so "
                    "it has to be larger than the start date."
                )
        return self

    @field_validator('transparency', mode='after')
    @classmethod
    def transparency_valid(cls, v: str) -> str:
        """
        Validate transparency settings in Google Calendar Event.
        """
        if v not in ['transparent', 'opaque']:
            raise ValueError(
                'Transparency of Google Calendar event can only be "transparent" or "opaque".'
            )
        return v

    def payload(self):
        """pydantic provides method json() that serializes our model, especially datetime objects are converted
        to the isoformat sring automatically! For example, if a is an instance of GoogleCalEvent, we get sth like

        a.json(by_alias=True) = '{"start": {"date": null, "dateTime": "2011-11-04T00:05:23+04:00", "timeZone": null},
                                  "end": {"date": null, "dateTime": "2011-11-05T00:05:23+04:00", "timeZone": null},
                                  "summary": "Calender event",
                                  'transparency': 'transparent'}'
        We convert this json string back to a dictionary. This creates None type objects in places where we had string
        'null' before - however, this is what is accepted by the api client (tested).
        """
        return json.loads(self.model_dump_json(by_alias=True))

    @staticmethod
    def from_rise_set(rise_set: RiseSet) -> 'GoogleCalEvent':
        """
        Create calendar event from a RiseSet event (e.g. sunrise, moonset ...).
        """
        symbol = '🌞' if rise_set.body == CelestialBody.SUN else '🌜'
        direction = '↑' if rise_set.rise else '↓'

        summary = (
            f"{symbol}{direction} at {rise_set.event_time.strftime('%I:%M %p')}"
        )

        return GoogleCalEvent(
            start=GoogleCalTime(datetime=rise_set.event_time),
            end=GoogleCalTime(datetime=rise_set.event_time),
            summary=summary,
            transparency='transparent',
        )

    @staticmethod
    def from_moon_phase(moon_phase: MoonPhase) -> 'GoogleCalEvent':
        """
        Create calendar event from a MoonPhase event. We are using an all-day event for that purpose.
        """
        event_date = moon_phase.event_time.date()
        timezone = moon_phase.timezone

        symbol = MOON_PHASE_SYMBOLS[moon_phase.phase_idx]
        desc = MOON_PHASES[moon_phase.phase_idx]

        summary = (
            f"{symbol} {desc} at {moon_phase.event_time.strftime('%I:%M %p')}"
        )

        return GoogleCalEvent(
            start=GoogleCalTime(date=event_date, timezone=timezone),
            end=GoogleCalTime(
                date=event_date + dt.timedelta(days=1), timezone=timezone
            ),
            summary=summary,
            transparency='transparent',
        )

    @staticmethod
    def from_magic_hour(magic_hour: MagicHour) -> 'GoogleCalEvent':

        symbol = '🌇' if magic_hour.color == 'golden' else '🏙'
        desc = 'Golden Hour' if magic_hour.color == 'golden' else 'Blue Hour'

        return GoogleCalEvent(
            start=GoogleCalTime(datetime=magic_hour.start),
            end=GoogleCalTime(datetime=magic_hour.end),
            summary=f'{symbol} {desc}',
            transparency='transparent',
        )

    @staticmethod
    def from_celestial_event(
        c_event: MoonPhase | RiseSet | MagicHour,
    ) -> 'GoogleCalEvent':
        """
        Interface method that calls either constructor 'from_rise_set' or 'from_moon_phase' depending on input type.
        """
        if isinstance(c_event, MoonPhase):
            return GoogleCalEvent.from_moon_phase(c_event)
        elif isinstance(c_event, RiseSet):
            return GoogleCalEvent.from_rise_set(c_event)
        elif isinstance(c_event, MagicHour):
            return GoogleCalEvent.from_magic_hour(c_event)
        else:
            raise NotImplementedError(
                'This method currently only supports events of type MoonPhase, RiseSet or MagicHour.'
            )


def get_sun_calendar_id(
    calendar_title: str, timezone: str, creds: Credentials
) -> str:
    """
    Get id of Google Calendar with name [calendar_title]. If no calendar with this name exists, create a new one.
    """

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


def request_calendars(creds: Credentials) -> dict[str, str]:
    """
    Get all existing calendars of this Google account.
    """

    with build("calendar", "v3", credentials=creds) as service:

        # use calendar id as key and calendar summary as value in this dict (summary would be more handy as key,
        # but unfortunately calendar titles don"t have to be unique (verified!)
        calendars: dict[str, str] = {}
        # response can have several pages (i.e. there is a max number of entries per page)
        page_token = None
        try:
            while True:
                calendar_list = (
                    # pylint: disable=maybe-no-member"
                    service.calendarList()
                    .list(pageToken=page_token)
                    .execute()
                )
                for entry in calendar_list['items']:
                    calendars[entry['id']] = entry['summary']

                page_token = calendar_list.get('nextPageToken')
                if not page_token:
                    break
        except HttpError as error:
            print(
                f'HTTP error {error.status_code} occured during the request for the list of existing \
                  Google Calendars. Reason: {error.reason}.\nExiting.'
            )
            sys.exit(1)

    return calendars


def create_sun_calendar(
    calendar_title: str, timezone: str, creds: Credentials
) -> str:
    """
    Create a new Google Calendar with title [calendar_title] in timezone [timezone].
    """

    with build("calendar", "v3", credentials=creds) as service:
        calendar = {"summary": calendar_title, "timeZone": timezone}
        try:
            # pylint: disable=maybe-no-member"
            created_calendar = (
                service.calendars().insert(body=calendar).execute()
            )
        except HttpError as error:
            print(
                f"HTTP error {error.status_code} occured during the creation of the new Google Calendar '{calendar_title}'. \
                  Reason: {error.reason}.\nExiting."
            )
            sys.exit(1)
        print(f"Created new Google Calendar named '{calendar_title}'.")

    return created_calendar["id"]


def export_events_to_google_calendar(
    google_calendar_id: str,
    events: list[GoogleCalEvent],
    credentials: Credentials,
) -> None:
    """
    Add events to Google Calendar with id [google_calendar_id]. Operate in batches of 1000.
    """

    # create batches of events list of max size 1000 (current max of Google api)
    event_batches = create_batches(list_=events, batch_size=1000)
    batch_count = len(event_batches)
    error_count = 0
    with build("calendar", "v3", credentials=credentials) as service:

        for batch_number, event_batch in enumerate(event_batches, 1):
            # pylint: disable=maybe-no-member"
            batch_request = (
                service.new_batch_http_request()
            )  # creates a BatchHttpRequest object
            for google_cal_event in event_batch:
                batch_request.add(
                    # pylint: disable=maybe-no-member"
                    service.events().insert(
                        calendarId=google_calendar_id,
                        body=google_cal_event.payload(),
                    )
                )
            try:
                batch_request.execute()
            except HttpError as error:
                error_count += 1
                print(
                    f"HTTP error {error.status_code} occured during the batch request \
                      {batch_number}/{batch_count} for creating calendar events. \
                      Reason: {error.reason}."
                )

        if error_count:
            if error_count == batch_count:
                print(
                    "All batch requests failed. No calendar events created. Exiting."
                )
            sys.exit(1)

        print("Creation of calendar events successful.")
