from timezonefinder import TimezoneFinder
from tests.test_data import CITIES

def test_timezonefinder():
    tf = TimezoneFinder()

    for city in CITIES:
        assert tf.timezone_at(lng = city['long'], lat = city['lat']) == city['timezone']

    # test a small town, Zahna
    assert tf.timezone_at(lng=12.785, lat=51.916) == 'Europe/Berlin'
