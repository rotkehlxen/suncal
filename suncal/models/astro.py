import datetime as dt

from astral import LocationInfo
from astral.location import Location

from typing import Dict


class Celestial:

    def __init__(self, timezone, date, longitude, latitude):
        self.timezone: str = timezone
        self.date: dt.date = date
        self.longitude: float = longitude
        self.latitude: float = latitude
        self.info: LocationInfo = self._get_info()
        self.location: Location = self._get_location()
        self.event: Dict[str, Dict] = self._get_event()

    def _get_info(self) -> LocationInfo:
        # name and region are of no consequence to any of the calculations
        return LocationInfo(
            timezone=self.timezone,
            latitude=self.latitude,
            longitude=self.longitude,
            name="undefined_name",
            region="undefined_region",
        )

    def _get_location(self) -> Location:
        return Location(self.info)

    def _get_event(self) -> Dict[str, Dict]:
        sunrise = self.location.sunrise(date=self.date)
        sunset = self.location.sunset(date=self.date)
        goldenhour_start, goldenhour_end = self.location.golden_hour(
            date=self.date
        )

        return {
            "sunrise": {"start": sunrise, "end": sunrise},
            "sunset": {"start": sunset, "end": sunset},
            "goldenhour": {"start": goldenhour_start, "end": goldenhour_end},
        }

    def gcal_summary(self) -> Dict[str, str]:
        """Create google calendar event summary.
           Export time in format '06:00 AM'. """

        return {
            "sunrise": f"↑🌞 {self.event['sunrise']['start'].strftime('%I:%M %p')}",
            "sunset": f"↑🌞 {self.event['sunset']['start'].strftime('%I:%M %p')}",
            "goldenhour": "📷 Golden Hour"
        }
