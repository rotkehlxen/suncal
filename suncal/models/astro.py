import datetime as dt

from astral import LocationInfo
from astral import SunDirection
from astral.location import Location
from pydantic import BaseModel  # pylint: disable=E0611


class Celestial(BaseModel):
    timezone: str
    date: dt.date
    longitude: float
    latitude: float

    @property
    def info(self):
        # name and region are of no consequence to any of the calculations
        return LocationInfo(
            timezone=self.timezone,
            latitude=self.latitude,
            longitude=self.longitude,
            name="undefined_name",
            region="undefined_region",
        )

    @property
    def location(self):
        return Location(self.info)

    @property
    def event(self):
        sunrise = self.location.sunrise(date=self.date)
        sunset = self.location.sunset(date=self.date)
        (
            golden_hour_morning_start,
            golden_hour_morning_end,
        ) = self.location.golden_hour(
            date=self.date, direction=SunDirection.RISING
        )
        (
            golden_hour_evening_start,
            golden_hour_evening_end,
        ) = self.location.golden_hour(
            date=self.date, direction=SunDirection.SETTING
        )

        return {
            "sunrise": {
                "start": sunrise,
                "end": sunrise,
                "gcal_summary": f"↑🌞 {sunrise.strftime('%I:%M %p')}",
            },
            "sunset": {
                "start": sunset,
                "end": sunset,
                "gcal_summary": f"↓🌞 {sunset.strftime('%I:%M %p')}",
            },
            "golden-hour-morning": {
                "start": golden_hour_morning_start,
                "end": golden_hour_morning_end,
                "gcal_summary": "📷 Golden Hour",
            },
            "golden-hour-evening": {
                "start": golden_hour_evening_start,
                "end": golden_hour_evening_end,
                "gcal_summary": "📷 Golden Hour",
            },
        }
