import datetime as dt

# locations, date 9.3.2023, sun/moon rise & set according to timeanddate.com (tad) in local time
berlin = {
    'lat': 52.520008,
    'long': 13.404954,
    'timezone': 'Europe/Berlin',
    'sunrise': dt.time(6, 35),
    'sunset': dt.time(17, 59),
    'moonrise': dt.time(20, 17),
    'moonset': dt.time(7, 26),
}

redwoodcity = {
    'lat': 37.4848,
    'long': -122.2281,
    'timezone': 'America/Los_Angeles',
    'sunrise': dt.time(6, 28),
    'sunset': dt.time(18, 10),
    'moonrise': dt.time(20, 33),
    'moonset': dt.time(7, 40),
}

punta_arenas = {
    'lat': -53.163833,
    'long': -70.917068,
    'timezone': 'America/Punta_Arenas',
    'sunrise': dt.time(7, 24),
    'sunset': dt.time(20, 22),
    'moonrise': dt.time(21, 12),
    'moonset': dt.time(9, 33),
}
maputo = {
    'lat': -25.966667,
    'long': 32.583333,
    'timezone': 'Africa/Maputo',
    'sunrise': dt.time(5, 47),
    'sunset': dt.time(18, 12),
    'moonrise': dt.time(19, 28),
    'moonset': dt.time(7, 15),
}

auckland = {
    'lat': -36.848461,
    'long': 174.763336,
    'timezone': 'Pacific/Auckland',
    'sunrise': dt.time(7, 13),
    'sunset': dt.time(19, 49),
    'moonrise': dt.time(20, 46),
    'moonset': dt.time(8, 23),
}

CITIES = [berlin, redwoodcity, punta_arenas, maputo, auckland]
