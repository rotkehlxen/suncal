import datetime as dt
from pydantic import BaseModel
from astral import LocationInfo
from astral.location import Location


class Celestial(BaseModel):
    timezone: str
    date: dt.date
    longitude: float
    latitude: float

    @property
    def info(self):
        # name and region are of no consequence to any of the calculations
        return LocationInfo(timezone=self.timezone,
                            latitude=self.latitude,
                            longitude=self.longitude,
                            name='undefined_name',
                            region='undefined_region')

    @property
    def location(self):
        return Location(self.info)

    @property
    def event(self):
        sunrise = self.location.sunrise(self.date)
        sunset = self.location.sunset(self.date)
        goldenhour = self.location.golden_hour(self.date)

        return {
            'sunrise': {'start': sunrise, 'end': sunrise},
            'sunset':  {'start': sunset, 'end': sunset},
            'goldenhour': {'start': goldenhour[0], 'end': goldenhour[1]},
        }
