import datetime as dt
from enum import Enum
from typing import Optional

import pytz
from pydantic import BaseModel  # pylint: disable=E0611
from pydantic import validator
from skyfield import almanac
from skyfield import api as skyfield_api

from suncal.utils import time_range_of_date

MOON_PHASE_SYMBOLS = ['🌚', '🌓', '🌝', '🌗']


class Location(BaseModel):
    """
    Location defined by latitude and longitude and local timezone.
    """
    timezone: str
    latitude: float
    longitude: float


class Event(Enum):
    """
    Enum class for the different celestial events that can be calculated.
    """
    SUNRISE = 'sunrise'
    SUNSET = 'sunset'
    MOONRISE = 'moonrise'
    MOONSET = 'moonset'
    MOONPHASE = 'moonphase'
    GOLDEN_HOUR_MORNING = 'golden_hour_morning'
    GOLDEN_HOUR_EVENING = 'golden_hour_evening'
    BLUE_HOUR_MORNING = 'blue_hour_morning'
    BLUE_HOUR_EVENING = 'blue_hour_evening'


class CelestialBody(Enum):
    """
    Enum class for the different celestial bodies that can be calculated.
    """
    SUN = 'sun'
    MOON = 'moon'


class RiseSet(BaseModel):
    """
    Model for rise and set events of the sun and the moon.
    """
    location: Location
    event_time: dt.datetime
    body: CelestialBody
    rise: bool


class MoonPhase(BaseModel):
    """
    Model for the main moon phases.
    The field phase_idx indicated the MoonPhase of interest:

    0 : 'New Moon'
    1 : 'First Quarter'
    2 : 'Full Moon'
    3 : 'Last Quarter'
    """

    timezone: str
    event_time: dt.datetime
    phase_idx: int

    @validator('phase_idx')
    def moon_phase_valid(cls, phase_idx):
        if phase_idx not in range(4):
            raise ValueError(
                'The phase_idx has to be either 0, 1, 2 or 3. This is the convention of skyfield '
                'for identification of the 4 main moon phases'
            )
        return phase_idx


class MagicHour(BaseModel):
    """
    Model for the Golden and Blue Hour.
    """
    color: str  # either golden or blue
    start: dt.datetime
    end: dt.datetime
    morning: bool  # in the morning or in the evening

    @validator('color')
    def color_valid(cls, color):
        if color not in ['golden', 'blue']:
            raise ValueError(
                'Color of the light in the Magic Hour can only be "blue" or "golden"'
            )
        return color


def calculate_rise_set(
    date: dt.date, location: Location, rise: bool, body: CelestialBody
) -> Optional[RiseSet]:
    """
    Calculate sun/moon rise/set. Only return a RiseSet event if the body rises/sets on the given date.
    """

    # period of time to scan for rise and set events
    t_start, t_end = time_range_of_date(date=date, timezone=location.timezone)

    eph = skyfield_api.load('de421.bsp')
    skyfield_location = skyfield_api.wgs84.latlon(
        location.latitude, location.longitude
    )

    if body == CelestialBody.SUN:
        f = almanac.sunrise_sunset(eph, skyfield_location)
    else:
        assert (
            body == CelestialBody.MOON
        ), "No rising/setting implementation for bodies other than sun or moon"
        f = almanac.risings_and_settings(eph, eph['moon'], skyfield_location)

    ts = skyfield_api.load.timescale()
    t, y = almanac.find_discrete(
        ts.from_datetime(t_start), ts.from_datetime(t_end), f
    )

    idx = 1 if rise else 0

    if idx not in y:
        print(
            f"The {body.value} does not {'rise' if rise else 'set'} on {date.strftime('%d.%m.%Y')}"
        )
        return None
    else:
        t_skyfield = t[y == idx]
        event_time = t_skyfield.astimezone(
            pytz.timezone(location.timezone)
        ).item()

        return RiseSet(
            location=location, event_time=event_time, body=body, rise=rise
        )


def calculate_magic_hour(
    date: dt.date, location: Location, color: str, morning: bool
) -> Optional[MagicHour]:
    """
    The golden hour starts with the center of the sun 4 degrees below the horizon and ends when the center of the sun
    is 6 degrees above the horizon. Similar for the Blue hour: it starts with the sun at 8 degrees below the
    horizon and ends with 4 degrees below.

    We only return a MagicHour object if both start and end time are available.
    """

    idx = 1 if morning else 0

    degree = {'blue': {'from': -8, 'to': -4}, 'golden': {'from': -4, 'to': 6}}

    t_start, t_end = time_range_of_date(date=date, timezone=location.timezone)

    eph = skyfield_api.load('de421.bsp')
    skyfield_location = skyfield_api.wgs84.latlon(
        location.latitude, location.longitude
    )

    ts = skyfield_api.load.timescale()
    t, y = almanac.find_discrete(
        ts.from_datetime(t_start),
        ts.from_datetime(t_end),
        almanac.risings_and_settings(
            eph,
            eph['sun'],
            skyfield_location,
            horizon_degrees=degree[color]['from'],
        ),
    )
    if idx not in y:
        return None
    else:
        t_skyfield = t[y == idx]
        t1 = t_skyfield.astimezone(pytz.timezone(location.timezone)).item()

        t, y = almanac.find_discrete(
            ts.from_datetime(t_start),
            ts.from_datetime(t_end),
            almanac.risings_and_settings(
                eph,
                eph['sun'],
                skyfield_location,
                horizon_degrees=degree[color]['to'],
            ),
        )

        if idx not in y:
            return None
        else:
            t_skyfield = t[y == idx]
            t2 = t_skyfield.astimezone(pytz.timezone(location.timezone)).item()

            return MagicHour(
                start=t1 if morning else t2,
                end=t2 if morning else t1,
                color=color,
                morning=morning,
            )


def calculate_moon_phase(date: dt.date, timezone: str) -> Optional[MoonPhase]:
    """
    In general, we can calculate a moon phase (angle between 0 and 360 deg) for every single second. This function here
    does not return the phase, but only returns a MoonPhase object when we have either First Quarter, Full Moon, Last
    Quarter or New Moon on the provided date.

    Note: The moon phase is the same for every location on earth, however, it appears differently visually.
    """
    # period of time to scan for rise and set events
    t_start, t_end = time_range_of_date(date=date, timezone=timezone)
    eph = skyfield_api.load('de421.bsp')
    ts = skyfield_api.load.timescale()

    t, y = almanac.find_discrete(
        ts.from_datetime(t_start),
        ts.from_datetime(t_end),
        almanac.moon_phases(eph),
    )

    if len(y) == 0:
        # this will happen most of the time (there are only 4 days in a month with a "special moon phase")
        return None
    else:
        event_time = t.astimezone(pytz.timezone(timezone)).item()
        phase_idx = y.item()

        return MoonPhase(
            timezone=timezone, event_time=event_time, phase_idx=phase_idx
        )


CALC = {
    'sunrise': lambda date, location: calculate_rise_set(
        date=date, location=location, rise=True, body=CelestialBody.SUN
    ),
    'sunset': lambda date, location: calculate_rise_set(
        date=date, location=location, rise=False, body=CelestialBody.SUN
    ),
    'moonrise': lambda date, location: calculate_rise_set(
        date=date, location=location, rise=True, body=CelestialBody.MOON
    ),
    'moonset': lambda date, location: calculate_rise_set(
        date=date, location=location, rise=False, body=CelestialBody.MOON
    ),
    'moonphase': lambda date, location: calculate_moon_phase(
        date=date, timezone=location.timezone
    ),
    'golden_hour_morning': lambda date, location: calculate_magic_hour(
        date=date, location=location, color='golden', morning=True
    ),
    'golden_hour_evening': lambda date, location: calculate_magic_hour(
        date=date, location=location, color='golden', morning=False
    ),
    'blue_hour_morning': lambda date, location: calculate_magic_hour(
        date=date, location=location, color='blue', morning=True
    ),
    'blue_hour_evening': lambda date, location: calculate_magic_hour(
        date=date, location=location, color='blue', morning=False
    ),
}
