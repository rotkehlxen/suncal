import datetime as dt

from astral import LocationInfo
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
        golden_hour_start, golden_hour_end = self.location.golden_hour(
            date=self.date
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
                "gcal_summary": f"↑🌞 {sunset.strftime('%I:%M %p')}",
            },
            "goldenhour": {
                "start": golden_hour_start,
                "end": golden_hour_end,
                "gcal_summary": "📷 Golden Hour",
            },
        }
