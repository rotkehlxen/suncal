import datetime as dt

import numpy as np
import pytz
from pydantic import BaseModel  # pylint: disable=E0611
from skyfield import almanac
from skyfield import api as skyfield_api
from skyfield.timelib import Timescale

from suncal.utils import tz_aware_dt


def rise_set_dict(
    skyfield_t: Timescale, skyfield_y: np.ndarray, timezone: str
) -> dict:
    """
    The skyfield routine almanac.find_discrete() returns a tuple of t and y. t is a Timescale object and can hold
    multiple timestamps. y is an array of 0s and 1s where 0s indicate set and 1s indicate rise events. y serves as
    annotation for the timestamps contained within t.

    This function takes info from y and t and converts it to a dict like this:

    {'rise': datetime.datetime(2023, 3, 9, 6, 28, 55, 659694, tzinfo=<DstTzInfo 'US/Pacific' PST-1 day, 16:00:00 STD>),
     'set': datetime.datetime(2023, 3, 9, 18, 10, 25, 138982, tzinfo=<DstTzInfo 'US/Pacific' PST-1 day, 16:00:00 STD>)}

    Important
    1) we assume that t and y hold 2 events tops, i.e. one "rise" and one "set" event at most (ok because we calculate
       these events for each and every day separately and sun and moon rise only once per day)
    2) if rise and/or set is missing, we make sure to fill in missing keys and add values None
    """

    lut = {0: 'set', 1: 'rise'}
    t_in_zone = skyfield_t.astimezone(pytz.timezone(timezone))

    events = {
        lut[skyfield_y[idx]]: t_in_zone[idx] for idx in range(len(skyfield_y))
    }
    if 'set' not in events:
        events.update({'set': None})
    if 'rise' not in events:
        events.update({'rise': None})

    return events


class Celestial(BaseModel):
    timezone: str
    date: dt.date
    longitude: float
    latitude: float

    @property
    def events(self):

        ts = (
            skyfield_api.load.timescale()
        )  # representation of time within skyfield
        eph = skyfield_api.load(
            'de421.bsp'
        )  # ephemeris containing coordinates of stars and planets

        location = skyfield_api.wgs84.latlon(self.latitude, self.longitude)

        # period of time to scan for rise and set events
        t_start = tz_aware_dt(
            dt.datetime(
                year=self.date.year,
                month=self.date.month,
                day=self.date.day,
            ),
            timezone=self.timezone,
        )

        t_end = t_start + dt.timedelta(days=1, microseconds=-1)

        # calculate sunrise and sunset
        t_sun, y_sun = almanac.find_discrete(
            ts.from_datetime(t_start),
            ts.from_datetime(t_end),
            almanac.sunrise_sunset(eph, location),
        )
        sun_events = rise_set_dict(
            skyfield_t=t_sun, skyfield_y=y_sun, timezone=self.timezone
        )

        sunrise = sun_events['rise']
        sunset = sun_events['set']

        # calculate moonrise and moonset
        t_moon, y_moon = almanac.find_discrete(
            ts.from_datetime(t_start),
            ts.from_datetime(t_end),
            almanac.risings_and_settings(eph, eph['moon'], location),
        )

        moon_events = rise_set_dict(
            skyfield_t=t_moon, skyfield_y=y_moon, timezone=self.timezone
        )

        moonrise = moon_events['rise']
        moonset = moon_events['set']

        return {
            "sunrise": {
                "start": sunrise,
                "end": sunrise,
                "gcal_summary": f"🌞↑ {sunrise.strftime('%I:%M %p')}"
                if sunrise
                else None,
            },
            "sunset": {
                "start": sunset,
                "end": sunset,
                "gcal_summary": f"🌞↓ {sunset.strftime('%I:%M %p')}"
                if sunset
                else None,
            },
            "moonrise": {
                "start": moonrise,
                "end": moonrise,
                "gcal_summary": f"🌜↑ {moonrise.strftime('%I:%M %p')}"
                if moonrise
                else None,
            },
            "moonset": {
                "start": moonset,
                "end": moonset,
                "gcal_summary": f"🌜↓ {moonset.strftime('%I:%M %p')}"
                if moonset
                else None,
            },
        }
